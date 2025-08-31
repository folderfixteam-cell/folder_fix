//<!-- Scroll effect -->
"use strict";

// ==================== Auto-show modals ====================
window.addEventListener("load", function () {
  const modalEls = Array.from(
    document.querySelectorAll('.modal[data-autoshow="true"]')
  );
  if (!modalEls.length) return;

  if (typeof bootstrap === "undefined") {
    alert(
      modalEls
        .map((el) => {
          const body = el.querySelector(".modal-body");
          return body ? body.textContent.trim() : "";
        })
        .join("\n\n")
    );
    return;
  }

  function showNext(i) {
    if (i >= modalEls.length) return;
    const el = modalEls[i];
    const m = new bootstrap.Modal(el);
    el.addEventListener(
      "hidden.bs.modal",
      function () {
        showNext(i + 1);
      },
      { once: true }
    );
    m.show();
  }
  showNext(0);
});

// ==================== Search + highlight ====================
document.addEventListener("DOMContentLoaded", () => {
  const searchBox = document.getElementById("searchBox");
  const comboItems = document.querySelectorAll(".combo-item");
  const notFound = document.getElementById("notFound");

  if (!searchBox || comboItems.length === 0) return;

  comboItems.forEach((item) => {
    const p = item.querySelector("p");
    if (p && !p.dataset.orig) p.dataset.orig = p.textContent;
  });

  const highlight = (text, query) => {
    const esc = query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const re = new RegExp(`(${esc})`, "ig");
    return text.replace(re, `<span class="highlight">$1</span>`);
  };

  searchBox.addEventListener("input", function () {
    const q = this.value.trim().toLowerCase();
    let any = false;

    comboItems.forEach((item) => {
      const p = item.querySelector("p");
      if (!p) return;
      const orig = p.dataset.orig || p.textContent;
      const hay = orig.toLowerCase();

      if (!q) {
        p.innerHTML = orig;
        item.style.display = "";
        any = true;
        return;
      }

      if (hay.includes(q)) {
        p.innerHTML = highlight(orig, q);
        item.style.display = "";
        any = true;
      } else {
        p.innerHTML = orig;
        item.style.display = "none";
      }
    });

    if (notFound) notFound.style.display = any ? "none" : "block";
  });
});

// ==================== Active section marker ====================
document.addEventListener("DOMContentLoaded", () => {
  const sections = document.querySelectorAll("main section[id]");
  const navLinks = document.querySelectorAll(".sidebar .nav-link");
  if (sections.length === 0 || navLinks.length === 0) return;

  const map = new Map();
  navLinks.forEach((link) => {
    const href = link.getAttribute("href") || "";
    if (href.startsWith("#")) map.set(href.slice(1), link);
  });

  const onIntersect = (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const id = entry.target.id;
        navLinks.forEach((l) => l.classList.remove("active"));
        const active = map.get(id);
        if (active) active.classList.add("active");
      }
    });
  };

  const io = new IntersectionObserver(onIntersect, {
    root: null,
    rootMargin: "0px 0px -60% 0px",
    threshold: 0.25,
  });

  sections.forEach((sec) => io.observe(sec));
});

// ==================== Chart.js charts ====================
document.addEventListener("DOMContentLoaded", () => {
  if (typeof Chart === "undefined") return;

  const membershipCanvas = document.getElementById("membershipChart");
  if (membershipCanvas) {
    const ctx = membershipCanvas.getContext("2d");
    new Chart(ctx, {
      type: "line",
      data: {
        labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        datasets: [
          {
            label: "Members",
            data: [120, 150, 180, 220, 260, 300],
            backgroundColor: "rgba(13,110,253,0.2)",
            borderColor: "rgba(13,110,253,1)",
            borderWidth: 2,
            tension: 0.3,
            fill: true,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        animation: { duration: 300 },
      },
    });
  }

  const revenueCanvas = document.getElementById("revenueChart");
  if (revenueCanvas) {
    const ctx = revenueCanvas.getContext("2d");
    new Chart(ctx, {
      type: "bar",
      data: {
        labels: ["Week 1", "Week 2", "Week 3", "Week 4"],
        datasets: [
          {
            label: "Revenue ₹",
            data: [3000, 4500, 7000, 5000],
            backgroundColor: "rgba(255,193,7,0.7)",
            borderColor: "rgba(255,193,7,1)",
            borderWidth: 1,
            borderRadius: 5,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } },
        animation: { duration: 300 },
      },
    });
  }
});

// ==================== Razorpay flow ====================
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("payForm");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    try {
      const resp = await fetch(form.action, {
        method: "POST",
        headers: { "X-Requested-With": "XMLHttpRequest" },
        body: new FormData(form),
      });

      if (!resp.ok) throw new Error("Failed to create order");
      const data = await resp.json();

      if (typeof Razorpay === "undefined") {
        alert(
          "Payment library not loaded. Please check your network and try again."
        );
        return;
      }

      const options = {
        key: data.razorpay_key_id,
        amount: data.amount,
        currency: data.currency,
        name: "Membership",
        description: "Monthly membership (30 days)",
        order_id: data.order_id,
        handler: async function (response) {
          try {
            const fd = new FormData();
            fd.append("razorpay_order_id", response.razorpay_order_id);
            fd.append("razorpay_payment_id", response.razorpay_payment_id);
            fd.append("razorpay_signature", response.razorpay_signature);

            const v = await fetch("/member/verify/", { // replace with your verify endpoint
              method: "POST",
              body: fd,
            });

            if (!v.ok) throw new Error("Verification failed");
            alert("Payment successful. Reloading…");
            location.reload();
          } catch (err) {
            console.error(err);
            alert(
              "Payment captured, but verification failed. Contact support."
            );
          }
        },
        prefill: {
          email: "", // set dynamically if needed
          name: "", // set dynamically if needed
        },
        theme: { color: "#0a66c2" },
      };

      const rzp = new Razorpay(options);
      rzp.open();
    } catch (err) {
      console.error(err);
      alert("Unable to start payment right now. Please try again later.");
    }
  });
});

$(window).on("scroll", function () {
    if ($(this).scrollTop() > 50) {
        $("#mainNavbar").addClass("navbar-scroll");
    } else {
        $("#mainNavbar").removeClass("navbar-scroll");
    }
});


