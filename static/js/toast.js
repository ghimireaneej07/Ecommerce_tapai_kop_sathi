/**
 * Tapai Ko Sathi - Toast Notification System
 * Lightweight, nature-inspired feedback system.
 */

const toastContainer = document.createElement('div');
toastContainer.className = 'tks-toast-container';
document.body.appendChild(toastContainer);

window.showToast = function (options) {
    const { title, message, type = 'success', duration = 4000 } = options;

    const toast = document.createElement('div');
    toast.className = `tks-toast tks-toast-${type}`;

    let icon = '🌿';
    if (type === 'error') icon = '⚠️';
    if (type === 'info') icon = '💡';

    toast.innerHTML = `
        <div class="tks-toast-icon">${icon}</div>
        <div class="tks-toast-content">
            <span class="tks-toast-title">${title}</span>
            <span class="tks-toast-message">${message}</span>
        </div>
    `;

    toastContainer.appendChild(toast);

    // Trigger entrance animation
    setTimeout(() => toast.classList.add('show'), 10);

    // Auto-remove
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 400);
    }, duration);
};
