(function(){
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  document.addEventListener('click', function(e){
    const el = e.target.closest && e.target.closest('.cm-toggle');
    if(!el) return;
    e.preventDefault();
    const pk = el.dataset.pk;
    if(!confirm('Voulez-vous vraiment basculer l\'état lu/non-lu pour ce message ?')) return;
    const url = el.getAttribute('href');
    fetch(url, {
      method: 'GET',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': getCookie('csrftoken')
      },
      credentials: 'same-origin'
    }).then(function(resp){
      if(resp.ok){
        // reload the page to reflect change
        window.location.reload();
      } else {
        alert('Erreur lors de la mise à jour.');
      }
    }).catch(function(){
      alert('Erreur réseau lors de la mise à jour.');
    });
  });
})();
