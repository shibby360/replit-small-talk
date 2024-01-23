window.onblur = function() {
  fetch('/editprof/online/False/'+localStorage.getItem('username'))
}
window.onfocus = function() {
  fetch('/editprof/online/True/'+localStorage.getItem('username'))
}