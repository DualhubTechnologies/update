(function () {

  const sidebar = document.getElementById('sidebar');
  const appShell = document.querySelector('.app-shell');
  const desktopToggle = document.getElementById('sidebarToggle');
  const mobileToggle = document.getElementById('sidebarMobileToggle');

  const desktopMQ = window.matchMedia('(min-width: 992px)');
  const mobileMQ = window.matchMedia('(max-width: 991.98px)');

  if (!sidebar || !appShell) return;

  /* =====================================================
     HELPERS
  ===================================================== */

  function closeAllSubmenus() {
    sidebar.querySelectorAll('.collapse.show').forEach(el => {
      el.classList.remove('show');
      el.style.height = null;
    });

    sidebar.querySelectorAll('.submenu-toggle[aria-expanded="true"]').forEach(toggle => {
      toggle.setAttribute('aria-expanded', 'false');
    });
  }

  function setMini(isMini) {
    if (isMini) {
      appShell.classList.add('sidebar-mini');
      localStorage.setItem('sidebarMini', '1');
      closeAllSubmenus();
    } else {
      appShell.classList.remove('sidebar-mini');
      localStorage.setItem('sidebarMini', '0');
    }
  }

  /* =====================================================
     INITIAL STATE (DESKTOP ONLY)
  ===================================================== */

  const savedState = localStorage.getItem('sidebarMini');

  if (desktopMQ.matches) {
    if (savedState === '1') {
      setMini(true);
    } else {
      setMini(false);
    }
  }

  /* =====================================================
     DESKTOP TOGGLE
  ===================================================== */

  if (desktopToggle) {
    desktopToggle.addEventListener('click', function () {
      const isMini = appShell.classList.contains('sidebar-mini');
      setMini(!isMini);
    });
  }

  /* =====================================================
     MOBILE TOGGLE (OFFCANVAS BEHAVIOR)
  ===================================================== */

  if (mobileToggle) {
    mobileToggle.addEventListener('click', function () {
      sidebar.classList.toggle('show');
    });
  }

  /* =====================================================
     CLICK OUTSIDE (MOBILE CLOSE)
  ===================================================== */

  document.addEventListener('click', function (e) {
    if (!mobileMQ.matches) return;

    const clickedInside =
      sidebar.contains(e.target) ||
      (mobileToggle && mobileToggle.contains(e.target));

    if (!clickedInside) {
      sidebar.classList.remove('show');
    }
  });

  /* =====================================================
     PREVENT SUBMENU TOGGLE IN MINI MODE
  ===================================================== */

  document.addEventListener('click', function (e) {
    const toggle = e.target.closest('.submenu-toggle');
    if (!toggle) return;

    if (appShell.classList.contains('sidebar-mini')) {
      e.preventDefault();
      e.stopPropagation();
    }
  });

  /* =====================================================
     HANDLE RESIZE (DESKTOP <-> MOBILE)
  ===================================================== */

  window.addEventListener('resize', function () {

    if (desktopMQ.matches) {
      sidebar.classList.remove('show');

      // Restore saved mini state
      const saved = localStorage.getItem('sidebarMini');
      if (saved === '1') {
        setMini(true);
      } else {
        setMini(false);
      }

    } else {
      // On mobile remove mini mode entirely
      appShell.classList.remove('sidebar-mini');
      sidebar.classList.remove('show');
    }
  });

})();