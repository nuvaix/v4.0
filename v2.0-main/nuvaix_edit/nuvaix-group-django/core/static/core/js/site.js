(() => {
  'use strict';

  const root = document.documentElement;
  const header = document.querySelector('[data-header]');
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#main-nav');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

  // A compact sticky header that gains depth as the page moves.
  const updateHeader = () => header?.classList.toggle('is-scrolled', window.scrollY > 12);
  updateHeader();
  window.addEventListener('scroll', updateHeader, { passive: true });

  // Accessible mobile navigation.
  const closeNav = () => {
    nav?.classList.remove('is-open');
    toggle?.setAttribute('aria-expanded', 'false');
    document.body.classList.remove('nav-open');
  };
  toggle?.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') === 'true';
    toggle.setAttribute('aria-expanded', String(!open));
    nav?.classList.toggle('is-open', !open);
    document.body.classList.toggle('nav-open', !open);
  });
  nav?.querySelectorAll('a').forEach(link => link.addEventListener('click', closeNav));
  window.addEventListener('resize', () => { if (window.innerWidth > 900) closeNav(); }, { passive: true });
  document.addEventListener('keydown', event => { if (event.key === 'Escape') closeNav(); });

  // A site-wide cinematic reveal system. Every page's main header gets a subtle
  // 3D flip-in; sections and cards reveal with staggered movement as they enter view.
  const motionTargets = [...document.querySelectorAll(
    'main > section, main .section-heading, main .intro-layout, main .feature-layout, ' +
    'main .about-columns, main .detail-layout, main .business-card, main .tech-cards article, ' +
    'main .value-list article, main .contact-form, main .content-card, main .detail-card, ' +
    'main .directory-card, main .project-card, main .insight-card, main .paint-info-card, ' +
    'main .legal-note, main .empty-state'
  )];
  const heroHeadings = document.querySelectorAll('.page-hero h1, .paint-hero h1, .hero-slide h1');

  if (!reduceMotion.matches && 'IntersectionObserver' in window) {
    motionTargets.forEach((element, index) => {
      if (element.dataset.motionReady) return;
      element.dataset.motionReady = 'true';
      element.classList.add('motion-in');
      element.style.setProperty('--motion-delay', `${Math.min(index % 5, 4) * 75}ms`);
      const mode = index % 4;
      if (mode === 1) element.classList.add('motion-from-left');
      else if (mode === 2) element.classList.add('motion-from-right');
      else if (mode === 3) element.classList.add('motion-from-depth');
    });
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('motion-visible', 'is-visible');
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -5% 0px' });
    motionTargets.forEach(element => observer.observe(element));

    const gsapAvailable = Boolean(window.gsap && window.ScrollTrigger);
    if (gsapAvailable) {
      window.gsap.registerPlugin(window.ScrollTrigger);
      document.querySelectorAll('.page-hero h1, .paint-hero h1').forEach(heading => {
        window.gsap.fromTo(heading,
          { opacity: 0, rotateX: -16, y: 38, transformPerspective: 1200, transformOrigin: '50% 0%' },
          { opacity: 1, rotateX: 0, y: 0, duration: 1.05, delay: 0.08, ease: 'power3.out',
            scrollTrigger: { trigger: heading, start: 'top 91%', once: true } }
        );
      });
    }
    heroHeadings.forEach((heading, index) => {
      if (gsapAvailable && !heading.closest('.hero-slide')) return;
      heading.classList.add('motion-in', 'motion-flip');
      heading.style.setProperty('--motion-delay', `${Math.min(index, 2) * 110}ms`);
      if (heading.getBoundingClientRect().top < window.innerHeight * 0.92) {
        requestAnimationFrame(() => heading.classList.add('motion-visible'));
      } else {
        const headingObserver = new IntersectionObserver(entries => {
          if (entries.some(entry => entry.isIntersecting)) {
            heading.classList.add('motion-visible');
            headingObserver.disconnect();
          }
        }, { threshold: 0.1 });
        headingObserver.observe(heading);
      }
    });
  } else {
    motionTargets.forEach(element => element.classList.add('motion-visible', 'is-visible'));
    heroHeadings.forEach(element => element.classList.add('motion-visible'));
  }

  // Gold reading-progress line.
  const progress = document.createElement('div');
  progress.className = 'scroll-progress';
  progress.setAttribute('aria-hidden', 'true');
  document.body.prepend(progress);
  let progressQueued = false;
  const updateProgress = () => {
    const range = document.documentElement.scrollHeight - window.innerHeight;
    progress.style.transform = `scaleX(${range > 0 ? Math.min(1, Math.max(0, window.scrollY / range)) : 0})`;
    progressQueued = false;
  };
  window.addEventListener('scroll', () => {
    if (progressQueued) return;
    progressQueued = true;
    window.requestAnimationFrame(updateProgress);
  }, { passive: true });
  window.addEventListener('resize', updateProgress, { passive: true });
  updateProgress();

  // Pointer-responsive 3D surfaces. Disabled for touch and reduced-motion users.
  if (finePointer && !reduceMotion.matches) {
    document.querySelectorAll(
      '.business-card, .directory-card, .project-card, .insight-card, .tech-cards article, ' +
      '.paint-info-card, .content-card, .detail-card'
    ).forEach(card => {
      card.classList.add('tilt-card');
      card.addEventListener('pointermove', event => {
        const bounds = card.getBoundingClientRect();
        if (!bounds.width || !bounds.height) return;
        const x = (event.clientX - bounds.left) / bounds.width;
        const y = (event.clientY - bounds.top) / bounds.height;
        card.style.setProperty('--tilt-x', `${(0.5 - y) * 7}deg`);
        card.style.setProperty('--tilt-y', `${(x - 0.5) * 9}deg`);
        card.style.setProperty('--glow-x', `${x * 100}%`);
        card.style.setProperty('--glow-y', `${y * 100}%`);
      });
      card.addEventListener('pointerleave', () => {
        card.style.setProperty('--tilt-x', '0deg');
        card.style.setProperty('--tilt-y', '0deg');
      });
    });
  }

  // Home hero uses a 3D flip/tilt transition rather than the previous flat fade.
  const slider = document.querySelector('[data-hero-slider]');
  if (slider) {
    const slides = [...slider.querySelectorAll('[data-slide]')];
    const dots = [...slider.querySelectorAll('[data-slide-dot]')];
    const count = slider.querySelector('[data-slide-count]');
    const previous = slider.querySelector('[data-slide-prev]');
    const next = slider.querySelector('[data-slide-next]');
    let active = Math.max(0, slides.findIndex(slide => slide.classList.contains('is-active')));
    let timer = null;

    const show = index => {
      active = (index + slides.length) % slides.length;
      slides.forEach((slide, i) => {
        const selected = i === active;
        slide.classList.toggle('is-active', selected);
        slide.setAttribute('aria-hidden', String(!selected));
        if (selected) slide.removeAttribute('inert');
        else slide.setAttribute('inert', '');
      });
      dots.forEach((dot, i) => {
        const selected = i === active;
        dot.classList.toggle('is-active', selected);
        dot.setAttribute('aria-current', String(selected));
      });
      if (count) count.textContent = String(active + 1).padStart(2, '0');
    };
    const stop = () => { if (timer) window.clearInterval(timer); timer = null; };
    const start = () => {
      stop();
      if (!reduceMotion.matches && !document.hidden) timer = window.setInterval(() => show(active + 1), 6500);
    };
    previous?.addEventListener('click', () => { show(active - 1); start(); });
    next?.addEventListener('click', () => { show(active + 1); start(); });
    dots.forEach((dot, i) => dot.addEventListener('click', () => { show(i); start(); }));
    slider.addEventListener('mouseenter', stop);
    slider.addEventListener('mouseleave', start);
    slider.addEventListener('focusin', stop);
    slider.addEventListener('focusout', event => { if (!slider.contains(event.relatedTarget)) start(); });
    document.addEventListener('visibilitychange', () => document.hidden ? stop() : start());
    reduceMotion.addEventListener?.('change', start);
    show(active);
    start();
  }

  // Smooth page-leave curtain for local navigation; external links behave normally.
  const curtain = document.querySelector('.page-transition');
  if (curtain && !reduceMotion.matches) {
    document.querySelectorAll('a[href]').forEach(link => {
      const href = link.getAttribute('href');
      if (!href || href.startsWith('#') || link.target === '_blank' || link.hasAttribute('download')) return;
      let target;
      try { target = new URL(href, window.location.href); } catch { return; }
      if (target.origin !== window.location.origin || target.pathname === window.location.pathname && target.search === window.location.search) return;
      link.addEventListener('click', event => {
        if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        curtain.classList.add('is-leaving');
        window.setTimeout(() => { window.location.href = target.href; }, 260);
      });
    });
  }

  document.querySelectorAll('form.contact-form').forEach(form => {
    form.addEventListener('submit', event => { if (!form.reportValidity()) event.preventDefault(); });
  });

  // Accessible floating social menu: click to toggle, Escape/outside click to close.
  const socialFloat = document.querySelector('[data-social-float]');
  if (socialFloat) {
    const socialToggle = socialFloat.querySelector('.social-toggle');
    const socialPanel = socialFloat.querySelector('#social-panel');
    const setSocialOpen = open => {
      socialFloat.classList.toggle('is-open', open);
      socialToggle.setAttribute('aria-expanded', String(open));
      socialToggle.setAttribute('aria-label', open ? 'Close social media links' : 'Open social media links');
      socialPanel.setAttribute('aria-hidden', String(!open));
      if (open) socialPanel.removeAttribute('inert');
      else socialPanel.setAttribute('inert', '');
    };
    socialToggle.addEventListener('click', () => {
      setSocialOpen(socialToggle.getAttribute('aria-expanded') !== 'true');
    });
    document.addEventListener('pointerdown', event => {
      if (!socialFloat.contains(event.target)) setSocialOpen(false);
    });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && socialToggle.getAttribute('aria-expanded') === 'true') {
        setSocialOpen(false);
        socialToggle.focus();
      }
    });
    socialPanel.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => setSocialOpen(false));
    });
  }

  // Keep all visible content accessible and usable when the browser restores a page.
  window.addEventListener('pageshow', () => curtain?.classList.remove('is-leaving'));
  root.classList.add('js-ready');
})();
