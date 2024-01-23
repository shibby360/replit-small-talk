fetch('https://www.cloudflare.com/cdn-cgi/trace').then(function(response) {
  response.text().then(function(data) {
    data = data.trim().split('\n').reduce(function(obj, pair) {
      pair = pair.split('=');
      return obj[pair[0]] = pair[1], obj;
    }, {});
    var userdict = JSON.parse(localStorage.getItem('stuff'))
    document.getElementById('flag').src = userdict.location.flag
  })
})