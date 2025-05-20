
function getTime(){
var today = new Date();
var time = today.getHours() + ":" + today.getMinutes();
console.log(time);
return time;
}
time = getTime();
document.getElementById('zeit').textContent = `time `+ String(time);
setInterval(function(){
time = getTime();
document.getElementById('zeit').textContent = `time `+ String(time);
}, 10000);