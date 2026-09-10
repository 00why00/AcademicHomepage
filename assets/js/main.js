import { loadCitations } from "./citations.js";

document.documentElement.classList.replace("no-js", "js");

// Preserve external-link behavior without changing internal navigation targets.
for (const link of document.querySelectorAll("a[href]")) {
  if (["http:", "https:"].includes(link.protocol) && link.origin !== location.origin && !link.hasAttribute("target")) {
    link.target = "_blank";
    link.relList.add("noopener");
  }
}

const nav = document.getElementById("site-nav");
const toggle = nav?.querySelector(".site-nav__toggle");
const links = document.getElementById("navigation-links");
const desktop = window.matchMedia("(min-width: 57.8125em)");

if (nav && toggle && links) {
  toggle.hidden = false;

  function closeMenu(restoreFocus = false) {
    links.classList.remove("is-open");
    toggle.setAttribute("aria-expanded", "false");
    if (restoreFocus) toggle.focus();
  }

  toggle.addEventListener("click", () => {
    const open = toggle.getAttribute("aria-expanded") !== "true";
    toggle.setAttribute("aria-expanded", String(open));
    links.classList.toggle("is-open", open);
  });

  nav.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
      closeMenu(true);
    }
  });

  links.addEventListener("click", (event) => {
    const link = event.target.closest("a");
    if (!link) return;
    const targetURL = new URL(link.href);
    if (targetURL.origin === location.origin && targetURL.pathname === location.pathname) {
      const target = document.getElementById(decodeURIComponent(targetURL.hash.slice(1)));
      if (target) target.focus({ preventScroll: true });
    }
    closeMenu();
  });

  document.addEventListener("click", (event) => {
    if (!nav.contains(event.target)) closeMenu();
  });
  nav.addEventListener("focusout", (event) => {
    if (!nav.contains(event.relatedTarget)) closeMenu();
  });
  desktop.addEventListener("change", () => closeMenu());
}

const settings = document.querySelector("script[data-citation-source]")?.dataset;
void loadCitations(document, [settings?.citationSource, settings?.citationApi, settings?.citationFallback]);
