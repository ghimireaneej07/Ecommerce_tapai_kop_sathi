// Global JS for Tapai Ko Sathi

function tksGetCsrfToken() {
  const name = "csrftoken=";
  const cookies = document.cookie ? document.cookie.split(";") : [];
  for (let i = 0; i < cookies.length; i++) {
    const c = cookies[i].trim();
    if (c.startsWith(name)) {
      return decodeURIComponent(c.substring(name.length));
    }
  }
  return "";
}

// Toast Notification System
function tksShowToast(message, type = 'success') {
    let container = document.querySelector('.tks-toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'tks-toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `tks-toast ${type}`;
    toast.innerHTML = `
        <span class="tks-toast-icon">${type === 'success' ? '✓' : '✕'}</span>
        <span class="tks-toast-message">${message}</span>
    `;

    container.appendChild(toast);

    // Remove after 3 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function tksRefreshCartBadge() {
  const endpoints = window.TKS_CART_ENDPOINTS || {};
  if (!endpoints.detail) return;
  
  fetch(endpoints.detail, { credentials: "same-origin" })
    .then((r) => r.json())
    .then((data) => {
      const count = data.total_items || 0;
      document
        .querySelectorAll(".tks-cart-link")
        .forEach((el) => (el.textContent = `Cart (${count})`));
    })
    .catch(() => {});
}

document.addEventListener("DOMContentLoaded", function () {
  // Smooth scroll
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener("click", function (e) {
      const targetId = this.getAttribute("href").substring(1);
      const target = document.getElementById(targetId);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: "smooth" });
      }
    });
  });

  const endpoints = window.TKS_CART_ENDPOINTS || {};

  // Add to cart buttons
  document.querySelectorAll(".tks-btn-add-cart").forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      e.preventDefault(); // Prevent default if inside a link
      const productId = this.getAttribute("data-product-id");
      
      if (!endpoints.add || !productId) return;

      const originalText = this.textContent;
      this.textContent = "Adding...";
      this.classList.add("loading");
      this.disabled = true;

      fetch(`${endpoints.add}${productId}/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": tksGetCsrfToken(),
          "X-Requested-With": "XMLHttpRequest",
        },
        credentials: "same-origin",
      })
        .then((r) => {
            if (!r.ok) throw new Error("Failed");
            return r.json();
        })
        .then(() => {
          tksRefreshCartBadge();
          tksShowToast("Item added to cart successfully!");
        })
        .catch(() => {
          tksShowToast("Could not add to cart. Please try again.", "error");
        })
        .finally(() => {
            this.textContent = originalText;
            this.classList.remove("loading");
            this.disabled = false;
        });
    });
  });

  // Remove from cart buttons (if verified to be on page)
  document.querySelectorAll(".tks-btn-remove-item").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const itemId = this.getAttribute("data-item-id");
      if (!endpoints.remove || !itemId) return;
      
      fetch(`${endpoints.remove}${itemId}/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": tksGetCsrfToken(),
          "X-Requested-With": "XMLHttpRequest",
        },
        credentials: "same-origin",
      })
        .then((r) => r.json())
        .then(() => {
          const row = document.querySelector(`tr[data-item-id="${itemId}"]`);
          if (row) row.remove();
          tksRefreshCartBadge();
          tksShowToast("Item removed from cart.");
        })
        .catch(() => {
          tksShowToast("Could not remove item.", "error");
        });
    });
  });

  tksRefreshCartBadge();
});
