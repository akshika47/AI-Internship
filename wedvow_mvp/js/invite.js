(function () {
  const cfg = window.WEDVOW_EVENT;
  if (!cfg) {
    console.error("WEDVOW_EVENT missing — load event-config.js first.");
    return;
  }

  const $ = (id) => document.getElementById(id);
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function setText(id, value) {
    const el = $(id);
    if (el && value != null) el.textContent = value;
  }

  function formatPhone(phone) {
    const digits = String(phone).replace(/\D/g, "");
    if (digits.length === 10) {
      return `${digits.slice(0, 3)} ${digits.slice(3, 6)} ${digits.slice(6)}`;
    }
    return phone;
  }

  function whatsappUrl(phone) {
    let digits = String(phone).replace(/\D/g, "");
    if (digits.length === 10 && digits.startsWith("0")) {
      digits = "27" + digits.slice(1);
    }
    const text = encodeURIComponent(
      `Hi, I'd like to RSVP for Washy's Golden Jubilee on ${cfg.dateLabel}.`
    );
    return `https://wa.me/${digits}?text=${text}`;
  }

  function bindContacts() {
    const wrap = $("rsvpContacts");
    if (!wrap) return;
    wrap.replaceChildren();
    (cfg.rsvpContacts || []).forEach((c) => {
      const card = document.createElement("div");
      card.className = "rsvp-contact-card";

      const name = document.createElement("strong");
      name.textContent = c.name;

      const actions = document.createElement("div");
      actions.className = "rsvp-actions";

      const call = document.createElement("a");
      call.className = "btn small";
      call.href = `tel:${String(c.phone).replace(/\s/g, "")}`;
      call.textContent = formatPhone(c.phone);

      const wa = document.createElement("a");
      wa.className = "btn secondary small";
      wa.href = whatsappUrl(c.phone);
      wa.target = "_blank";
      wa.rel = "noopener noreferrer";
      wa.textContent = "WhatsApp";

      actions.append(call, wa);
      card.append(name, actions);
      wrap.appendChild(card);
    });
  }

  function bindConfig() {
    document.title = `${cfg.headline} — ${cfg.subheadline || cfg.honoreeName}`;

    setText("sealMonogram", cfg.monogram);
    setText("envelopeName", cfg.honoreeName);
    setText("heroAge", cfg.subheadline);
    setText("dateBanner", cfg.dateLabel);
    setText("storyTitle", cfg.inviteLine);
    setText("detailDate", cfg.dateLabel);
    setText("detailTime", cfg.time);
    setText("detailVenue", cfg.venue);
    setText("detailDress", cfg.dressCode);
    setText("detailAddress", cfg.address);
    setText(
      "rsvpDeadline",
      cfg.rsvpDeadline ? `RSVP by ${cfg.rsvpDeadline}` : ""
    );
    setText("giftNote", cfg.giftNote || "");
    setText("hostLabel", cfg.hostLabel);
    setText("closeTitle", cfg.closingLine);
    setText(
      "locationLede",
      [cfg.venue, cfg.address].filter(Boolean).join(" · ")
    );

    const adults = $("adultsNote");
    if (adults) {
      if (cfg.adultsOnly) {
        adults.textContent = cfg.adultsOnlyNote || "NB: No kids allowed";
      } else {
        adults.classList.add("hidden");
      }
    }

    const meal = $("mealNote");
    if (meal) {
      if (cfg.mealNote) {
        meal.textContent = cfg.mealNote;
        meal.classList.remove("hidden");
      } else {
        meal.classList.add("hidden");
      }
    }

    const portrait = $("portraitImg");
    if (portrait && cfg.portraitImage) {
      portrait.src = cfg.portraitImage;
      portrait.alt = cfg.fullName || cfg.honoreeName;
    }

    const storyImg = $("storyImg");
    if (storyImg && cfg.heroImage) {
      storyImg.src = cfg.heroImage;
      storyImg.alt = cfg.fullName || cfg.honoreeName;
    }

    const mapsEmbed = $("mapsEmbed");
    if (mapsEmbed && cfg.mapsEmbedUrl) {
      mapsEmbed.src = cfg.mapsEmbedUrl;
    }

    const mapsLink = $("mapsLink");
    if (mapsLink && cfg.mapsLinkUrl) {
      mapsLink.href = cfg.mapsLinkUrl;
    }

    bindContacts();
  }

  function showInvite() {
    const envelope = $("envelope");
    const invite = $("invite");
    invite.hidden = false;
    requestAnimationFrame(() => invite.classList.add("is-visible"));
    envelope.classList.add("is-dismissed");
    setTimeout(() => {
      envelope.setAttribute("aria-hidden", "true");
      envelope.style.display = "none";
    }, reduceMotion ? 0 : 500);
  }

  function openEnvelope() {
    const card = $("envelopeCard");
    if (card.classList.contains("is-opened")) return;
    card.classList.add("is-opened");
    setTimeout(showInvite, reduceMotion ? 0 : 700);
  }

  function initEnvelope() {
    const card = $("envelopeCard");
    card.addEventListener("click", openEnvelope);
    card.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        openEnvelope();
      }
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && !$("envelope").classList.contains("is-dismissed")) {
        openEnvelope();
      }
    });
  }

  function initReveals() {
    const nodes = document.querySelectorAll(".reveal");
    if (reduceMotion || !("IntersectionObserver" in window)) {
      nodes.forEach((n) => n.classList.add("is-in"));
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-in");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.18, rootMargin: "0px 0px -8% 0px" }
    );
    nodes.forEach((n) => io.observe(n));
  }

  function initParallax() {
    const texture = $("heroTexture");
    if (!texture || reduceMotion) return;
    let ticking = false;
    window.addEventListener(
      "scroll",
      () => {
        if (ticking) return;
        ticking = true;
        requestAnimationFrame(() => {
          texture.style.setProperty(
            "--parallax",
            `${Math.min(window.scrollY * 0.18, 80)}px`
          );
          ticking = false;
        });
      },
      { passive: true }
    );
  }

  bindConfig();
  initEnvelope();
  initReveals();
  initParallax();
})();
