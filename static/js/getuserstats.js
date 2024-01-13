function login(usrnm, pwd) {
  var xhr = new XMLHttpRequest()
  localStorage.setItem('username', usrnm)
  xhr.open('GET', `/loggedin?user=${usrnm}&pwd=${pwd}`, true)
  xhr.send()
  xhr.onreadystatechange = processRequest
  function processRequest(e) {
    if (xhr.readyState == 4 && xhr.status == 200) {
      var response = xhr.responseText
      if(response === 'invalid auth') {
        alert('invalid auth')
        window.location.reload()
      } else {
        localStorage.setItem('stuff', response)
      }
    }
  }
}