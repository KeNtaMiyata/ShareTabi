window.twttr = (function(d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0],
      t = window.twttr || {};
    if (d.getElementById(id)) return t;
    js = d.createElement(s);
    js.id = id;
    js.src = "https://platform.twitter.com/widgets.js";
    fjs.parentNode.insertBefore(js, fjs);
  
    t._e = [];
    t.ready = function(f) {
      t._e.push(f);
    };
  
    return t;
  }(document, "script", "twitter-wjs"));


// for form js
// https://stackoverflow.com/questions/31224651/show-hide-password-onclick-of-button-using-javascript-only

function show() {
  var p = document.getElementById('pwd');
  p.setAttribute('type', 'text');
}

function hide() {
  var p = document.getElementById('pwd');
  p.setAttribute('type', 'password');
}

var pwShown = 0;

document.getElementById("eye").addEventListener("click", function () {
  if (pwShown == 0) {
      pwShown = 1;
      show();
  } else {
      pwShown = 0;
      hide();
  }
}, false);


// 添付した画像を表示
function previewImage(obj)
{
	var fileReader = new FileReader();
	fileReader.onload = (function() {
		document.getElementById('preview').src = fileReader.result;
	});
	fileReader.readAsDataURL(obj.files[0]);
}


// gabyoの色
// let gabyocolor;
// let rand=Math.floor(Math.random()*5);
// if (rand == 0) {
//     gabyocolor = "g-yellow";
// }
// if (rand == 1) {
//     gabyocolor = "g-pink";
// }
// if (rand == 2) {
//     gabyocolor = "g-red";
// }
// if (rand == 3) {
//     gabyocolor = "g-blue";
// }
// if (rand == 4) {
//     gabyocolor = "g-green";
// }
// document.getElementsByClassName("circle").classList.add(gabyocolor);


// 削除確認
function confirm_delete(){
  if (confirm( "削除してよいですか？" )){
      return true;
  }
  else{
      return false
  }
}
