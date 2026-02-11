    (function(){
      const sidebar = document.getElementById('sidebar');
      const desktopToggle = document.getElementById('sidebarToggle');
      const mobileToggle = document.getElementById('sidebarMobileToggle');

      function setMini(isMini){
        if(isMini){
          sidebar.classList.add('sidebar-mini');
          localStorage.setItem('sidebarMini', '1');
        }else{
          sidebar.classList.remove('sidebar-mini');
          localStorage.setItem('sidebarMini', '0');
        }
      }

      const saved = localStorage.getItem('sidebarMini');
      if(saved === '1' && window.matchMedia('(min-width: 992px)').matches){ setMini(true); }

      if(desktopToggle){
        desktopToggle.addEventListener('click', function(){
          const isMini = sidebar.classList.contains('sidebar-mini');
          setMini(!isMini);
        });
      }

      if(mobileToggle){
        mobileToggle.addEventListener('click', function(){
          sidebar.classList.toggle('show');
        });
      }

      document.addEventListener('click', function(e){
        if(window.matchMedia('(max-width: 991.98px)').matches){
          const isClickInside = sidebar.contains(e.target) || (mobileToggle && mobileToggle.contains(e.target));
          if(!isClickInside){ sidebar.classList.remove('show'); }
        }
      });
    })();