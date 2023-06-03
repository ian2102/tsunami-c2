const letters = "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZqwertyuiopasdfghjklzxcvbnm";
let intervals = {};

document.addEventListener("DOMContentLoaded", function() {
  var fontSize = localStorage.getItem('font_size') || '100';
  var filter = localStorage.getItem('filter') || '1';

  document.body.style.fontSize = fontSize + '%';
  document.body.style.filter = filter == '2' ? 'invert(1)' : 'none';
  const titleElements = document.querySelectorAll(".title");

  titleElements.forEach(titleElement => {
    let iteration = 0;
    const textContent = titleElement.textContent;

    clearInterval(intervals[titleElement]);

    intervals[titleElement] = setInterval(() => {
      titleElement.innerText = titleElement.innerText
        .split("")
        .map((letter, index) => {
          if(index < iteration) {
            return textContent[index];
          }
          
          return letters[Math.floor(Math.random() * 26)];
        })
        .join("");
      
      if(iteration >= textContent.length){ 
        clearInterval(intervals[titleElement]);
      }
      
      iteration += 1 / 3;
    }, 25);
  });
});
