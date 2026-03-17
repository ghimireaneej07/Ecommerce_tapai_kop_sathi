/**
 * Tapai Ko Sathi - AJAX Cart Interactivity
 * Handle add, remove, and update actions without page reloads.
 */

document.addEventListener('DOMContentLoaded', function () {
    // Intercept Add to Cart Forms
    const addForms = document.querySelectorAll('.tks-add-to-cart-form');

    addForms.forEach(form => {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            const formData = new FormData(this);
            const actionUrl = this.action;
            addToCart(actionUrl, formData);
        });
    });

    // Handle Direct Add Buttons (grid/detail)
    document.addEventListener('click', function (e) {
        // Handle Add
        const addBtn = e.target.closest('.tks-btn-add-cart');
        if (addBtn && !addBtn.closest('form')) {
            e.preventDefault();
            const productId = addBtn.dataset.productId;
            if (!productId) return;

            const url = window.TKS_CART_ENDPOINTS?.add ? `${window.TKS_CART_ENDPOINTS.add}${productId}/` : `/cart/api/add/${productId}/`;
            const formData = new FormData();
            formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));
            formData.append('quantity', 1);

            addToCart(url, formData);
        }

        // Handle Remove
        const removeBtn = e.target.closest('.tks-btn-remove-item');
        if (removeBtn) {
            e.preventDefault();
            const itemId = removeBtn.dataset.itemId;
            const url = window.TKS_CART_ENDPOINTS?.remove ? `${window.TKS_CART_ENDPOINTS.remove}${itemId}/` : `/cart/api/remove/${itemId}/`;

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
                .then(response => response.json())
                .then(data => {
                    const payload = data.data || data;
                    if (data.success) {
                        const itemRow = removeBtn.closest('.tks-cart-item');
                        itemRow.style.opacity = '0';
                        itemRow.style.transform = 'translateY(10px)';
                        setTimeout(() => {
                            itemRow.remove();
                            if ((payload.cart_item_count || 0) === 0) location.reload();
                            updateCartUI(payload);
                        }, 300);
                    }
                });
        }

        // Handle Quantity Adjust
        const qtyBtn = e.target.closest('.tks-qty-btn');
        if (qtyBtn) {
            const itemId = qtyBtn.dataset.itemId;
            const currentQtySpan = qtyBtn.parentElement.querySelector('.tks-item-qty');
            let newQty = parseInt(currentQtySpan.textContent);

            if (qtyBtn.classList.contains('tks-qty-inc')) newQty++;
            else if (qtyBtn.classList.contains('tks-qty-dec') && newQty > 1) newQty--;
            else return;

            currentQtySpan.textContent = newQty;

            const updateUrl = window.TKS_CART_ENDPOINTS?.update ? `${window.TKS_CART_ENDPOINTS.update}${itemId}/` : `/cart/api/update/${itemId}/`;
            fetch(updateUrl, {
                method: 'POST',
                body: JSON.stringify({ quantity: newQty }),
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
                .then(response => response.json())
                .then(data => {
                    const payload = data.data || data;
                    if (data.success) {
                        updateCartUI(payload);
                    } else {
                        showToast({ title: 'Error', message: data.message, type: 'error' });
                    }
                });
        }
    });

    function addToCart(url, formData) {
        fetch(url, {
            method: 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
            .then(response => response.json())
            .then(data => {
                const payload = data.data || data;
                if (data.success) {
                    showToast({
                        title: 'Selection Added',
                        message: data.message || 'Remedy added to your wellness kit.',
                        type: 'success'
                    });
                    updateCartCounter(payload.cart_item_count || 0);
                } else {
                    showToast({ title: 'Wellness Alert', message: data.message, type: 'error' });
                }
            });
    }

    function updateCartUI(data) {
        updateCartCounter(data.cart_item_count || 0);
        const subtotal = document.querySelector('.tks-cart-subtotal');
        const total = document.querySelector('.tks-cart-total');
        if (subtotal) subtotal.textContent = `NPR ${data.cart_total || '0.00'}`;
        if (total) total.textContent = `NPR ${data.cart_total || '0.00'}`;
        if (data.item_subtotal && data.item_id) {
            const item = document.querySelector(`.tks-cart-item[data-item-id="${data.item_id}"]`);
            if (item) {
                const sub = item.querySelector('[style*="font-weight: 700"]');
                if (sub) sub.textContent = `NPR ${data.item_subtotal}`;
            }
        }
    }

    function updateCartCounter(count) {
        let counter = document.querySelector('.tks-cart-counter');
        const cartLink = document.querySelector('.tks-cart-link');
        if (!counter && cartLink) {
            counter = document.createElement('span');
            counter.className = 'tks-cart-counter';
            Object.assign(counter.style, {
                position: 'absolute', top: '-8px', right: '-8px',
                background: 'var(--accent)', color: 'white', fontSize: '10px',
                padding: '2px 6px', borderRadius: '10px', fontWeight: '700'
            });
            cartLink.appendChild(counter);
        }
        if (counter) {
            counter.textContent = count;
            counter.style.display = count > 0 ? 'inline-block' : 'none';
        }
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
