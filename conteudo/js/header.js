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
/* =========================
     Menu Mobile (hambúrguer)
  ========================= */
document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.nav');

  if (!toggle || !nav) return;

  function closeMenu() {
    nav.classList.remove('open');
    toggle.classList.remove('open');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'Abrir menu');
  }

  toggle.addEventListener('click', (event) => {
    event.stopPropagation();

    const isOpen = nav.classList.toggle('open');

    toggle.classList.toggle('open', isOpen);
    toggle.setAttribute('aria-expanded', String(isOpen));
    toggle.setAttribute(
      'aria-label',
      isOpen ? 'Fechar menu' : 'Abrir menu'
    );
  });

  document.addEventListener('click', (event) => {
    const clickedInsideMenu = nav.contains(event.target);
    const clickedToggle = toggle.contains(event.target);

    if (
      nav.classList.contains('open') &&
      !clickedInsideMenu &&
      !clickedToggle
    ) {
      closeMenu();
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && nav.classList.contains('open')) {
      closeMenu();
      toggle.focus();
    }
  });

  nav.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => {
      if (!link.classList.contains('dropdown-toggle')) {
        closeMenu();
      }
    });
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const languageLinks = document.querySelectorAll(".header-languages a");

  languageLinks.forEach(function (link) {
    link.addEventListener("click", function (event) {
      const href = link.getAttribute("href") || "";

      let targetLang = null;

      if (href.includes("/en/")) {
        targetLang = "en";
      } else {
        targetLang = "pt-BR";
      }

      const alternate = document.querySelector(
        `link[rel="alternate"][hreflang="${targetLang}"]`
      );

      if (alternate && alternate.getAttribute("href")) {
        event.preventDefault();

        const alternateHref = alternate.getAttribute("href");

        try {
          const alternateUrl = new URL(alternateHref);

          if (
            window.location.hostname === "127.0.0.1" ||
            window.location.hostname === "localhost"
          ) {
            window.location.href = alternateUrl.pathname;
          } else {
            window.location.href = alternateUrl.href;
          }
        } catch (error) {
          window.location.href = alternateHref;
        }
      }
    });
  });
});
/*document.addEventListener("DOMContentLoaded", function () {

  const langContainer = document.querySelector(".header-languages");
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

  const backToTop = document.querySelector('.back-to-top');

  window.addEventListener('scroll', () => {
    if (window.scrollY > 200) {
      backToTop.classList.add('show');
    } else {
      backToTop.classList.remove('show');
    }
  });*/
