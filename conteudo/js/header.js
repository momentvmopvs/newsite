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

document.addEventListener("DOMContentLoaded", function () {

  const langContainer = document.querySelector(".lang");
  if (!langContainer) return;

  const ptLink = langContainer.querySelector('a[href="/"]');
  const enLink = langContainer.querySelector('a[href="/en/"]');

  function switchLanguage(targetLang) {
    let path = window.location.pathname;

    // Remove /en se existir
    if (path.startsWith("/en/")) {
      path = path.replace("/en", "");
    }

    // Se o destino for inglês, adiciona /en
    if (targetLang === "en") {
      path = "/en" + path;
    }

    window.location.href = path;
  }

  ptLink.addEventListener("click", function (e) {
    e.preventDefault();
    switchLanguage("pt");
  });

  enLink.addEventListener("click", function (e) {
    e.preventDefault();
    switchLanguage("en");
  });

});

const btn = document.querySelector('.back-to-top');

window.addEventListener('scroll', () => {
  btn.style.display = window.scrollY > 300 ? 'block' : 'none';
});

