(function () {
  const sidebar = document.getElementById('sidebar');
  const desktopToggle = document.getElementById('sidebarToggle');
  const mobileToggle = document.getElementById('sidebarMobileToggle');
  const desktopMQ = window.matchMedia('(min-width: 992px)');
  const mobileMQ = window.matchMedia('(max-width: 991.98px)');

  if (!sidebar) return;

  /* =====================================================
     HELPERS
  ===================================================== */
  function closeAllSubmenus() {
    // Close open collapse elements
    sidebar.querySelectorAll('.collapse.show').forEach(el => {
      el.classList.remove('show');
      el.style.height = null;
    });

    // Reset aria-expanded on toggles
    sidebar.querySelectorAll('.submenu-toggle[aria-expanded="true"]').forEach(toggle => {
      toggle.setAttribute('aria-expanded', 'false');
    });
  }

  function setMini(isMini) {
    if (isMini) {
      sidebar.classList.add('sidebar-mini');
      localStorage.setItem('sidebarMini', '1');

      // IMPORTANT: reset submenu state
      closeAllSubmenus();
    } else {
      sidebar.classList.remove('sidebar-mini');
      localStorage.setItem('sidebarMini', '0');
    }
  }

  /* =====================================================
     INITIAL STATE (DESKTOP ONLY)
  ===================================================== */
  const savedState = localStorage.getItem('sidebarMini');
  if (savedState === '1' && desktopMQ.matches) {
    setMini(true);
  }

  /* =====================================================
     DESKTOP TOGGLE
  ===================================================== */
  if (desktopToggle) {
    desktopToggle.addEventListener('click', function () {
      const isMini = sidebar.classList.contains('sidebar-mini');
      setMini(!isMini);
    });
  }

  /* =====================================================
     MOBILE TOGGLE
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
    if (mobileMQ.matches) {
      const clickedInside =
        sidebar.contains(e.target) ||
        (mobileToggle && mobileToggle.contains(e.target));

      if (!clickedInside) {
        sidebar.classList.remove('show');
      }
    }
  });

  /* =====================================================
     PREVENT SUBMENU TOGGLE IN MINI MODE
  ===================================================== */
  document.addEventListener('click', function (e) {
    const toggle = e.target.closest('.submenu-toggle');
    if (!toggle) return;

    if (sidebar.classList.contains('sidebar-mini')) {
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
    } else {
      sidebar.classList.remove('sidebar-mini');
    }
  });

})();