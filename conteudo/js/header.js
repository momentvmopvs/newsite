/*document.addEventListener('DOMContentLoaded', () => {

  /* =========================
     Menu Mobile
  ========================= *
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.nav');

  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      nav.classList.toggle('open');
      toggle.classList.toggle('active');
    });
  }

  /* =========================
     Dropdown no Mobile
  ========================= *
  const dropdownToggles = document.querySelectorAll('.dropdown-toggle');

  dropdownToggles.forEach(toggle => {
    toggle.addEventListener('click', e => {
      if (window.innerWidth <= 900) {
        e.preventDefault();

        const parent = toggle.closest('.dropdown');
        const submenu = parent?.querySelector('.dropdown-menu');

        if (submenu) {
          submenu.classList.toggle('open');
        }
      }
    });
  });

});*/
document.addEventListener('DOMContentLoaded', () => {

  /* =========================
     Menu Mobile (hambúrguer)
  ========================= */
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.nav');

  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      nav.classList.toggle('open');
    });
  }

});


