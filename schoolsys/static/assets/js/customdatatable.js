  (function(){
    const el = document.getElementById('sysdataTable');
    if(!el) return;
    new DataTable(el, {
      responsive: true,
      pageLength: 7,
      lengthMenu: [7, 10, 25, 50],
      ordering: true
    });
  })();