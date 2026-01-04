document.addEventListener('DOMContentLoaded', () => {

  /* =========================
     Menu Mobile
  ========================= */
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.nav');

  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      nav.classList.toggle('open');
    });
  }

  /* =========================
     Dropdown no Mobile
  ========================= */
  const dropdownItems = document.querySelectorAll('.dropdown-toggle');

  dropdownItems.forEach(item => {
    item.addEventListener('click', function (e) {
      if (window.innerWidth <= 900) {
        e.preventDefault();

        const submenu = this.nextElementSibling;
        if (submenu) {
          submenu.classList.toggle('open');
        }
      }
    });
  });

});
