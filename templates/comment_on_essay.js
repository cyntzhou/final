var title = document.getElementById("1");
var topic = document.getElementById("2");
var paragraphs = document.getElementsByName("paragraph");
var fields = document.getElementsByTagName("fieldset");

var contents = [title, topic];
for (var f = 0; f < fields.length; f++){
    contents.push(fields[f])
};
var current_p;

var highlight = function (e){
    this.classList.toggle('highlight');
    current_p = this;
    console.log(current_p);
};

var unhighlight = function (e){
    this.classList.toggle('unhighlight');
    current_p = null;
};

var remove = function (){
    var r = confirm("Would you like to remove this comment?");
    if (r == true){
	this.remove();
    }
};

var removeAll = function (){
    for (var i = 0; i < contents.length ; i++){
	contents[i].removeEventListener('mouseover', highlight);
	contents[i].removeEventListener('mouseout', unhighlight);
	contents[i].removeEventListener('click', ask);
    };
};

var ask = function (){
    num = current_p.id;
    var answer = confirm("Would you like to comment on this paragraph?");
    if (answer == true){
	field = fields[num-1];
	var form = document.createElement('form');
	form.method = "POST";
	var id = document.createElement('input');
	id.name = "id";
	id.value = num;
	id.type="hidden";
	form.appendChild(id);
	var comment = document.createElement('textarea');
	comment.name="comment";
	form.appendChild(comment);
	var subm = document.createElement('input');
	subm.name="button";
	subm.type="submit";
	subm.class="pure-button pure-button-primary";
	subm.value="Submit Comment";
	form.appendChild(subm);
	var canc = document.createElement('input');
	canc.name="button";
	canc.type="submit";
	canc.class="pure-button pure-button-primary";
	canc.value="Cancel";
	form.appendChild(canc);
	field.appendChild(form);
	removeAll();
    }else{
	return;
    }	      
};

var addAll = function (){
    for (var i = 0; i < contents.length ; i++){
	contents[i].addEventListener('mouseover', highlight);
	contents[i].addEventListener('mouseout', unhighlight);
	contents[i].addEventListener('click', ask);
    };
}();
