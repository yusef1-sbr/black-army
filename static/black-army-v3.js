
/* ============================================================================
   BLACK ARMY // INTERACTION SYSTEM V3
   Safe enhancement layer. Existing script.js continues to handle forms,
   notifications and original behavior; this file adds visual interactions.
   ============================================================================ */
(() => {
  "use strict";

  const ready = (fn) => {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn, { once: true });
    } else {
      fn();
    }
  };

  ready(() => {
    const body = document.body;
    const admin = !!document.querySelector(".admin-layout");
    const publicPage = !admin && !!document.querySelector(".hero");
    body.classList.toggle("is-admin", admin);
    body.classList.toggle("is-public", publicPage);

    installAtmosphere();
    installOwnerEntry();
    installRevealObserver();
    installActiveNavigation();
    installCardTilt();
    installButtonRipple();
    installScrollProgress();
    installAmbientStatus();

    if (publicPage) {
      installPublicEnhancements();
    }

    if (admin) {
      installAdminEnhancements();
    }

    if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      installPointerGlow();
    }
  });

  function installAtmosphere() {
    if (document.querySelector(".ba-v3-backdrop")) return;

    const wrap = document.createElement("div");
    wrap.className = "ba-v3-backdrop";
    wrap.innerHTML = `
      <div class="ba-v3-grid"></div>
      <div class="ba-v3-scan"></div>
      <div class="ba-v3-noise"></div>
      <div class="ba-v3-vignette"></div>
      <div class="ba-v3-progress"></div>
    `;
    document.body.prepend(wrap);

    const progress = wrap.querySelector(".ba-v3-progress");
    const update = () => {
      const doc = document.documentElement;
      const max = Math.max(1, doc.scrollHeight - window.innerHeight);
      const ratio = Math.min(1, Math.max(0, window.scrollY / max));
      progress.style.transform = `scaleX(${ratio})`;
    };
    window.addEventListener("scroll", update, { passive: true });
    update();
  }

  function installOwnerEntry() {
    const nav = document.getElementById("mainNav");
    if (nav && !nav.querySelector(".owner-entry")) {
      const link = document.createElement("a");
      link.className = "owner-entry";
      link.href = "/admin";
      link.innerHTML = "🔐 <span>ورود مالکین</span>";
      nav.appendChild(link);
    }

    const footer = document.querySelector(".site-footer");
    if (footer && !footer.querySelector(".ba-owner-footer")) {
      const box = document.createElement("div");
      box.className = "container ba-owner-footer";
      box.innerHTML = `
        <div class="ba-owner-footer-title">
          <span>🔐</span>
          <span>دسترسی خصوصی مالکین و مرکز مدیریت Black Army</span>
        </div>
        <a href="/admin">ورود به پنل مالکین →</a>
      `;
      const footerBottom = footer.querySelector(".footer-bottom");
      if (footerBottom) {
        footer.insertBefore(box, footerBottom);
      } else {
        footer.appendChild(box);
      }
    }
  }

  function installRevealObserver() {
    const elements = document.querySelectorAll(".reveal");
    if (!elements.length) return;

    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced || !("IntersectionObserver" in window)) {
      elements.forEach(el => el.classList.add("show"));
      return;
    }

    const observer = new IntersectionObserver((entries, obs) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("show");
        obs.unobserve(entry.target);
      });
    }, { threshold: 0.08, rootMargin: "0px 0px -30px 0px" });

    elements.forEach((el, index) => {
      el.style.transitionDelay = `${Math.min(index % 6, 5) * 45}ms`;
      observer.observe(el);
    });
  }

  function installActiveNavigation() {
    const nav = document.getElementById("mainNav");
    if (!nav) return;

    const links = [...nav.querySelectorAll('a[href^="#"]')];
    if (!links.length || !("IntersectionObserver" in window)) return;

    const sections = links
      .map(link => document.querySelector(link.getAttribute("href")))
      .filter(Boolean);

    const map = new Map();
    sections.forEach(section => {
      const link = links.find(item => item.getAttribute("href") === `#${section.id}`);
      if (link) map.set(section, link);
    });

    const observer = new IntersectionObserver(entries => {
      const visible = entries
        .filter(entry => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (!visible) return;
      links.forEach(link => link.classList.remove("is-active"));
      const active = map.get(visible.target);
      if (active) active.classList.add("is-active");
    }, { rootMargin: "-25% 0px -55% 0px", threshold: [0, .15, .4, .7] });

    sections.forEach(section => observer.observe(section));
  }

  function installCardTilt() {
    if (window.matchMedia("(max-width: 900px)").matches) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const cards = document.querySelectorAll(
      ".stat-card, .feature-card, .person-card, .member-card, .news-card, .honor-card, .timeline-card, .relation-panel"
    );

    cards.forEach(card => {
      card.addEventListener("pointermove", event => {
        const rect = card.getBoundingClientRect();
        const x = (event.clientX - rect.left) / rect.width;
        const y = (event.clientY - rect.top) / rect.height;
        const rx = (0.5 - y) * 4.5;
        const ry = (x - 0.5) * 6;
        card.style.transform = `perspective(900px) rotateX(${rx}deg) rotateY(${ry}deg) translateY(-5px)`;
      });
      card.addEventListener("pointerleave", () => {
        card.style.transform = "";
      });
    });
  }

  function installButtonRipple() {
    document.addEventListener("pointerdown", event => {
      const button = event.target.closest(".btn, .action-button, .danger-button, .success-button, .admin-notification-button, .icon-button");
      if (!button) return;

      const rect = button.getBoundingClientRect();
      const ripple = document.createElement("span");
      ripple.className = "ba-ripple";
      ripple.style.cssText = `
        position:absolute;
        width:20px;
        height:20px;
        border-radius:50%;
        left:${event.clientX - rect.left - 10}px;
        top:${event.clientY - rect.top - 10}px;
        background:rgba(255,255,255,.24);
        pointer-events:none;
        transform:scale(0);
        animation:ba-ripple .65s ease-out forwards;
        z-index:20;
      `;
      if (getComputedStyle(button).position === "static") button.style.position = "relative";
      button.appendChild(ripple);
      setTimeout(() => ripple.remove(), 700);
    });

    if (!document.getElementById("baRippleStyle")) {
      const style = document.createElement("style");
      style.id = "baRippleStyle";
      style.textContent = `@keyframes ba-ripple { to { transform:scale(12); opacity:0; } }`;
      document.head.appendChild(style);
    }
  }

  function installScrollProgress() {
    const grid = document.querySelector(".ba-v3-grid");
    if (!grid || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    let ticking = false;
    const update = () => {
      ticking = false;
      const y = Math.min(window.scrollY * .015, 28);
      grid.style.transform = `perspective(900px) rotateX(62deg) translateY(${22 + y}%)`;
    };
    window.addEventListener("scroll", () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(update);
    }, { passive: true });
  }

  function installAmbientStatus() {
    const header = document.querySelector(".site-header");
    if (!header || header.querySelector(".ba-live-chip")) return;

    const chip = document.createElement("div");
    chip.className = "ba-live-chip";
    chip.innerHTML = `<i></i><span>NETWORK ONLINE</span>`;
    chip.style.cssText = `display:none;`;
    header.appendChild(chip);
  }

  function installPointerGlow() {
    if (window.matchMedia("(max-width: 760px)").matches) return;
    let halo = document.querySelector(".ba-v3-cursor");
    if (!halo) {
      halo = document.createElement("div");
      halo.className = "ba-v3-cursor";
      document.body.appendChild(halo);
    }

    let tx = -100, ty = -100, cx = tx, cy = ty;
    const animate = () => {
      cx += (tx - cx) * .17;
      cy += (ty - cy) * .17;
      halo.style.left = `${cx}px`;
      halo.style.top = `${cy}px`;
      requestAnimationFrame(animate);
    };
    animate();

    window.addEventListener("pointermove", event => {
      tx = event.clientX;
      ty = event.clientY;
      halo.classList.add("active");
    }, { passive: true });
    window.addEventListener("pointerleave", () => halo.classList.remove("active"));
  }

  function installPublicEnhancements() {
    const hero = document.querySelector(".hero");
    if (!hero) return;

    // Create a small live status strip without altering any Flask content.
    if (!hero.querySelector(".ba-command-strip")) {
      const strip = document.createElement("div");
      strip.className = "ba-command-strip";
      strip.innerHTML = `
        <div><span class="dot"></span><b>SYSTEM</b><em>ONLINE</em></div>
        <div><b>SECURITY</b><em>ACTIVE</em></div>
        <div><b>NETWORK</b><em>CONNECTED</em></div>
      `;
      hero.appendChild(strip);
      injectPublicStripStyle();
    }

    // Add subtle parallax to hero glow elements.
    if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      let raf = 0;
      window.addEventListener("pointermove", event => {
        if (raf) return;
        raf = requestAnimationFrame(() => {
          raf = 0;
          const x = (event.clientX / window.innerWidth - .5) * 2;
          const y = (event.clientY / window.innerHeight - .5) * 2;
          const a = hero.querySelector(".glow-one");
          const b = hero.querySelector(".glow-two");
          if (a) a.style.translate = `${x * 12}px ${y * 10}px`;
          if (b) b.style.translate = `${x * -8}px ${y * -6}px`;
        });
      }, { passive: true });
    }

    // Add a soft active class to the first hero CTA on focus.
    document.querySelectorAll(".hero .btn").forEach(btn => {
      btn.addEventListener("focus", () => btn.classList.add("is-focused"));
      btn.addEventListener("blur", () => btn.classList.remove("is-focused"));
    });
  }

  function injectPublicStripStyle() {
    if (document.getElementById("baPublicStripStyle")) return;
    const style = document.createElement("style");
    style.id = "baPublicStripStyle";
    style.textContent = `
      .ba-command-strip {
        position:absolute;
        left:50%;
        bottom:26px;
        transform:translateX(-50%);
        z-index:12;
        display:flex;
        gap:8px;
        padding:7px;
        border:1px solid rgba(255,255,255,.06);
        border-radius:16px;
        background:rgba(8,9,11,.54);
        backdrop-filter:blur(18px);
        box-shadow:0 20px 55px rgba(0,0,0,.28), inset 0 1px rgba(255,255,255,.05);
      }
      .ba-command-strip > div {
        min-width:130px;
        padding:8px 10px;
        border-radius:11px;
        background:rgba(255,255,255,.022);
        display:flex;
        align-items:center;
        justify-content:center;
        gap:6px;
        color:#666a73;
        font-size:7px;
        letter-spacing:.12em;
      }
      .ba-command-strip b { color:#bfc1c6; font-size:8px; }
      .ba-command-strip em { color:#737780; font-style:normal; }
      .ba-command-strip .dot { width:5px; height:5px; border-radius:50%; background:#34e39a; box-shadow:0 0 12px rgba(52,227,154,.6); }
      @media(max-width:760px){
        .ba-command-strip { width:calc(100% - 28px); }
        .ba-command-strip > div { min-width:0; flex:1; padding-inline:6px; }
        .ba-command-strip em { display:none; }
      }
    `;
    document.head.appendChild(style);
  }

  function installAdminEnhancements() {
    const topbar = document.querySelector(".admin-topbar");
    const layout = document.querySelector(".admin-layout");
    if (!topbar || !layout) return;

    if (!topbar.querySelector(".ba-admin-mobile-toggle")) {
      const toggle = document.createElement("button");
      toggle.type = "button";
      toggle.className = "ba-admin-mobile-toggle";
      toggle.setAttribute("aria-label", "باز کردن منوی پنل");
      toggle.textContent = "☰";
      toggle.addEventListener("click", () => {
        document.body.classList.toggle("admin-sidebar-open");
      });
      const title = topbar.querySelector("div:first-child");
      if (title) title.prepend(toggle);
    }

    const sidebar = document.querySelector(".admin-sidebar");
    if (sidebar) {
      sidebar.addEventListener("click", event => {
        const link = event.target.closest('a[href^="#"]');
        if (link) document.body.classList.remove("admin-sidebar-open");
      });
    }

    const sectionLinks = document.querySelectorAll(".admin-nav a[href^='#']");
    const sections = [...sectionLinks]
      .map(link => document.querySelector(link.getAttribute("href")))
      .filter(Boolean);

    if (sections.length && "IntersectionObserver" in window) {
      const linksMap = new Map();
      sections.forEach(section => {
        const link = [...sectionLinks].find(a => a.getAttribute("href") === `#${section.id}`);
        if (link) linksMap.set(section, link);
      });
      const observer = new IntersectionObserver(entries => {
        const hit = entries.find(e => e.isIntersecting);
        if (!hit) return;
        sectionLinks.forEach(link => link.classList.remove("is-active"));
        const active = linksMap.get(hit.target);
        if (active) active.classList.add("is-active");
      }, { rootMargin: "-18% 0px -70% 0px", threshold: .03 });
      sections.forEach(section => observer.observe(section));
    }

    // Add a concise command chipbar beneath the topbar text.
    const titleWrap = topbar.querySelector(".admin-top-actions")?.previousElementSibling;
    if (titleWrap && !titleWrap.querySelector(".ba-admin-chipbar")) {
      const chips = document.createElement("div");
      chips.className = "ba-admin-chipbar";
      const join = document.getElementById("joinCount")?.textContent?.trim() || "0";
      const msg = document.getElementById("messageCount")?.textContent?.trim() || "0";
      chips.innerHTML = `
        <span class="ba-admin-chip">JOIN <strong>${escapeHtml(join)}</strong></span>
        <span class="ba-admin-chip">UNREAD <strong>${escapeHtml(msg)}</strong></span>
        <span class="ba-admin-chip">SESSION <strong>OWNER</strong></span>
      `;
      titleWrap.appendChild(chips);
    }

    const watermark = document.createElement("div");
    watermark.className = "ba-admin-watermark";
    watermark.textContent = "BLACK ARMY // OWNER CONTROL";
    document.body.appendChild(watermark);

    // Add gentle stagger to admin sections.
    document.querySelectorAll(".admin-section").forEach((section, index) => {
      section.style.setProperty("--ba-section-delay", `${Math.min(index, 9) * 35}ms`);
      section.classList.add("ba-enter");
      section.style.animationDelay = `var(--ba-section-delay)`;
    });
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>'"]/g, ch => ({
      "&":"&amp;", "<":"&lt;", ">":"&gt;", "'":"&#39;", "\"":"&quot;"
    }[ch]));
  }
})();
