/* ═══════════════════════════════════════════
   EXIA GHOST — Scroll-Driven Animation Engine
   GSAP + Lenis + Canvas Frame Rendering
   ═══════════════════════════════════════════ */

(() => {
  "use strict";

  // ── Config ──────────────────────────────
  const FRAME_COUNT = 169;
  const FRAME_SPEED = 0.944;
  const IMAGE_SCALE = 0.87;
  const FRAME_PATH = "frames/frame_";
  const FRAME_EXT = ".webp";

  // ── DOM refs ────────────────────────────
  const loader = document.getElementById("loader");
  const loaderBar = document.getElementById("loader-bar");
  const loaderPercent = document.getElementById("loader-percent");
  const heroSection = document.getElementById("hero");
  const canvasWrap = document.getElementById("canvas-wrap");
  const canvas = document.getElementById("canvas");
  const ctx = canvas.getContext("2d");
  const darkOverlay = document.getElementById("dark-overlay");
  const scrollContainer = document.getElementById("scroll-container");
  const marquee1 = document.getElementById("marquee-1");

  // ── State ───────────────────────────────
  const frames = [];
  let currentFrame = -1;
  let bgColor = "#0a0a0a";

  // ═══════════════════════════════════════
  // 1. FRAME PRELOADER (two-phase)
  // ═══════════════════════════════════════

  function framePath(i) {
    return FRAME_PATH + String(i).padStart(4, "0") + FRAME_EXT;
  }

  async function preloadFrames() {
    let loaded = 0;

    // Phase 1: First 10 frames immediately
    const phase1 = [];
    for (let i = 1; i <= Math.min(10, FRAME_COUNT); i++) {
      phase1.push(loadFrame(i));
    }
    await Promise.all(phase1);

    // Phase 2: Remaining frames
    for (let i = 11; i <= FRAME_COUNT; i++) {
      await loadFrame(i);
    }

    function loadFrame(index) {
      return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => {
          frames[index - 1] = img;
          loaded++;
          const pct = Math.round((loaded / FRAME_COUNT) * 100);
          loaderBar.style.width = pct + "%";
          loaderPercent.textContent = pct + "%";
          resolve();
        };
        img.onerror = () => {
          loaded++;
          resolve();
        };
        img.src = framePath(index);
      });
    }
  }

  // ═══════════════════════════════════════
  // 2. CANVAS RENDERER (padded cover)
  // ═══════════════════════════════════════

  function resizeCanvas() {
    const dpr = window.devicePixelRatio || 1;
    canvas.width = window.innerWidth * dpr;
    canvas.height = window.innerHeight * dpr;
    canvas.style.width = window.innerWidth + "px";
    canvas.style.height = window.innerHeight + "px";
    ctx.scale(dpr, dpr);
    if (currentFrame >= 0) drawFrame(currentFrame);
  }

  function sampleBgColor(img) {
    const tmp = document.createElement("canvas");
    tmp.width = 4; tmp.height = 4;
    const tctx = tmp.getContext("2d");
    tctx.drawImage(img, 0, 0, 4, 4);
    const d = tctx.getImageData(0, 0, 1, 1).data;
    return `rgb(${d[0]},${d[1]},${d[2]})`;
  }

  function drawFrame(index) {
    const img = frames[index];
    if (!img) return;

    const cw = window.innerWidth;
    const ch = window.innerHeight;
    const iw = img.naturalWidth;
    const ih = img.naturalHeight;
    const scale = Math.max(cw / iw, ch / ih) * IMAGE_SCALE;
    const dw = iw * scale;
    const dh = ih * scale;
    const dx = (cw - dw) / 2;
    const dy = (ch - dh) / 2;

    ctx.fillStyle = bgColor;
    ctx.fillRect(0, 0, cw, ch);
    ctx.drawImage(img, dx, dy, dw, dh);
  }

  // ═══════════════════════════════════════
  // 3. LENIS SMOOTH SCROLL
  // ═══════════════════════════════════════

  let lenis;

  function initLenis() {
    lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothWheel: true,
    });
    lenis.on("scroll", ScrollTrigger.update);
    gsap.ticker.add((time) => lenis.raf(time * 1000));
    gsap.ticker.lagSmoothing(0);
  }

  // ═══════════════════════════════════════
  // 4. SCROLL-DRIVEN ANIMATIONS
  // ═══════════════════════════════════════

  function initScrollAnimations() {
    gsap.registerPlugin(ScrollTrigger);

    // 4a. Frame-to-scroll binding
    ScrollTrigger.create({
      trigger: scrollContainer,
      start: "top top",
      end: "bottom bottom",
      scrub: true,
      onUpdate: (self) => {
        const accelerated = Math.min(self.progress * FRAME_SPEED, 1);
        const index = Math.min(
          Math.floor(accelerated * FRAME_COUNT),
          FRAME_COUNT - 1
        );
        if (index !== currentFrame) {
          currentFrame = index;
          requestAnimationFrame(() => drawFrame(currentFrame));
          // Sample bg color every 20 frames
          if (index % 20 === 0 && frames[index]) {
            bgColor = sampleBgColor(frames[index]);
          }
        }
      },
    });

    // 4b. Hero fade → Nexa fade-in
    ScrollTrigger.create({
      trigger: scrollContainer,
      start: "top top",
      end: "bottom bottom",
      scrub: true,
      onUpdate: (self) => {
        const p = self.progress;
        // Hero fades out progressively
        heroSection.style.opacity = Math.max(0, 1 - p * 8);
        // Canvas fades in dès le premier scroll, lentement
        const fadeProgress = Math.min(1, Math.max(0, p / 0.15));
        canvasWrap.style.opacity = fadeProgress;
      },
    });

    // 4c. Dark overlay
    initDarkOverlay(0.10, 0.93);

    // 4d. Marquee
    initMarquee();

    // 4e. Section animations
    document.querySelectorAll(".scroll-section").forEach(setupSection);

    // 4f. Counters — static values, no animation
  }

  // ── Dark overlay ────────────────────────

  function initDarkOverlay(enter, leave) {
    const fadeRange = 0.04;
    ScrollTrigger.create({
      trigger: scrollContainer,
      start: "top top",
      end: "bottom bottom",
      scrub: true,
      onUpdate: (self) => {
        const p = self.progress;
        let opacity = 0;
        if (p >= enter - fadeRange && p <= enter) {
          opacity = ((p - (enter - fadeRange)) / fadeRange) * 0.33;
        } else if (p > enter && p < leave) {
          opacity = 0.33;
        } else if (p >= leave && p <= leave + fadeRange) {
          opacity = 0.33 * (1 - (p - leave) / fadeRange);
        }
        darkOverlay.style.opacity = opacity;
      },
    });
  }

  // ── Marquee ─────────────────────────────

  function initMarquee() {
    const mText = marquee1.querySelector(".marquee-text");
    gsap.to(mText, {
      xPercent: -25,
      ease: "none",
      scrollTrigger: {
        trigger: scrollContainer,
        start: "top top",
        end: "bottom bottom",
        scrub: true,
      },
    });

    // Fade marquee in/out
    ScrollTrigger.create({
      trigger: scrollContainer,
      start: "top top",
      end: "bottom bottom",
      scrub: true,
      onUpdate: (self) => {
        const p = self.progress;
        let op = 0;
        if (p > 0.25 && p < 0.85) {
          op = 1;
          if (p < 0.30) op = (p - 0.25) / 0.05;
          if (p > 0.80) op = (0.85 - p) / 0.05;
        }
        marquee1.style.opacity = op;
      },
    });
  }

  // ── Section animation system ────────────

  function setupSection(section) {
    const type = section.dataset.animation;

    const children = section.querySelectorAll(
      ".section-label, .section-heading, .section-body, .section-note, " +
      ".stat, .competitive-table, .cta-heading, .cta-body, .cta-buttons, .cta-footer"
    );

    // Initial state — hidden
    gsap.set(children, { opacity: 0 });

    // Build animation based on type
    const animProps = { opacity: 1, stagger: 0.12, duration: 0.9, ease: "power3.out" };

    switch (type) {
      case "fade-up":
        gsap.set(children, { y: 50 });
        Object.assign(animProps, { y: 0 });
        break;
      case "slide-left":
        gsap.set(children, { x: -80 });
        Object.assign(animProps, { x: 0, stagger: 0.14 });
        break;
      case "slide-right":
        gsap.set(children, { x: 80 });
        Object.assign(animProps, { x: 0, stagger: 0.14 });
        break;
      case "scale-up":
        gsap.set(children, { scale: 0.85 });
        Object.assign(animProps, { scale: 1, duration: 1.0, ease: "power2.out" });
        break;
      case "stagger-up":
        gsap.set(children, { y: 60 });
        Object.assign(animProps, { y: 0, stagger: 0.15, duration: 0.8 });
        break;
      case "clip-reveal":
        gsap.set(children, { clipPath: "inset(100% 0 0 0)" });
        Object.assign(animProps, { clipPath: "inset(0% 0 0 0)", stagger: 0.15, duration: 1.2, ease: "power4.inOut" });
        break;
      default:
        gsap.set(children, { y: 40 });
        Object.assign(animProps, { y: 0, duration: 0.8 });
    }

    // Trigger when section enters viewport — plays once, stays visible
    ScrollTrigger.create({
      trigger: section,
      start: "top 80%",
      once: true,
      onEnter: () => {
        gsap.to(children, animProps);
      },
    });
  }

  // ── Counter animations ──────────────────

  function initCounters() {
    document.querySelectorAll(".stat-number").forEach((el) => {
      const target = parseFloat(el.dataset.value);
      const decimals = parseInt(el.dataset.decimals || "0");

      // Create ScrollTrigger for the parent stats section
      const parentSection = el.closest(".scroll-section");
      if (!parentSection) return;

      const enter = parseFloat(parentSection.dataset.enter) / 100;

      let animated = false;
      ScrollTrigger.create({
        trigger: scrollContainer,
        start: "top top",
        end: "bottom bottom",
        onUpdate: (self) => {
          if (self.progress >= enter && !animated) {
            animated = true;
            gsap.to(el, {
              duration: 2.5,
              ease: "power1.out",
              onUpdate: function () {
                const progress = this.progress();
                const current = target * progress;
                el.textContent = decimals > 0
                  ? current.toFixed(decimals)
                  : Math.round(current);
              },
            });
          }
        },
      });
    });
  }

  // ═══════════════════════════════════════
  // 5. INIT
  // ═══════════════════════════════════════

  async function init() {
    // Preload all frames
    await preloadFrames();

    // Sample initial bg color
    if (frames[0]) {
      bgColor = sampleBgColor(frames[0]);
    }

    // Setup canvas
    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);
    drawFrame(0);

    // Init smooth scroll
    initLenis();

    // Init scroll animations
    initScrollAnimations();

    // Hide loader
    loader.classList.add("hidden");
  }

  // Start
  init();
})();
