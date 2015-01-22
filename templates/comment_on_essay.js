var title = document.getElementById("title");
var topic = document.getElementById("topic");
var essay = document.getElementById("essay");
var contents = [title, topic, essay];

for (var i = 0 ; i < title.textContent.length; i++){
    console.log(i);
};
for (var i = 0; i < contents.length ; i++){
    contents[i].addEventListener('mouseover', function(e){
	this.classList.toggle('red');
    });
};
title.addEventListener('mouseover', function(e){
    this.classList.toggle('red');
});
title.addEventListener('mouseover', function(e){this.classList.toggle('red')});
