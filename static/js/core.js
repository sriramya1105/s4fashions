// ThreadCraft Apparel - Core Client Engine
const API_BASE = "/api/v1";

// State Management
let appState = {
    products: [],
    filteredProducts: [],
    cart: JSON.parse(localStorage.getItem("tc_cart") || "[]"),
    user: JSON.parse(localStorage.getItem("tc_user") || "null"),
    token: localStorage.getItem("tc_token") || null,
    selectedCategory: "",
    selectedSubcategory: "",
    selectedBrand: "",
    maxPrice: null,
    minRating: null,
    searchQuery: ""
};

// Initialize
document.addEventListener("DOMContentLoaded", () => {
    syncAuthHeader();
    updateCartCounter();
});

// Splash Screen Controller (Show once only when the website is first opened)
let splashTimer = null;

function dismissSplashNow() {
    const splash = document.getElementById("splash-screen");
    if (!splash) return;
    if (splashTimer) {
        clearTimeout(splashTimer);
        splashTimer = null;
    }
    sessionStorage.setItem("s4_splash_shown", "true");
    splash.classList.add("hidden");
    setTimeout(() => {
        splash.style.display = "none";
    }, 700);
}

function handleSplashScreen() {
    const splash = document.getElementById("splash-screen");
    if (!splash) return;

    // If splash has already been shown in this browser session, hide it immediately
    const hasBeenShown = sessionStorage.getItem("s4_splash_shown");
    if (hasBeenShown) {
        splash.style.display = "none";
        return;
    }

    // Mark as shown so it never displays again on page refresh or navigation
    sessionStorage.setItem("s4_splash_shown", "true");

    // Automatically transition to home after 5.5 seconds if user does not click 'Shop Now'
    splashTimer = setTimeout(() => {
        dismissSplashNow();
    }, 5500);
}

// Customer Profile Slide-Over Drawer Controller
function openProfileSidebar() {
    const backdrop = document.getElementById("profile-drawer-backdrop");
    const drawer = document.getElementById("profile-drawer-sidebar");
    if (backdrop && drawer) {
        backdrop.classList.add("open");
        drawer.classList.add("open");
        document.body.style.overflow = "hidden";
    }
}

function closeProfileSidebar() {
    const backdrop = document.getElementById("profile-drawer-backdrop");
    const drawer = document.getElementById("profile-drawer-sidebar");
    if (backdrop && drawer) {
        backdrop.classList.remove("open");
        drawer.classList.remove("open");
        document.body.style.overflow = "";
    }
}

// Authentication UI Sync across pages
function syncAuthHeader() {
    const authContainer = document.getElementById("header-auth-slot") || document.getElementById("user-profile-slot");
    if (!authContainer) return;

    if (appState.user && appState.token) {
        const initial = (appState.user.username || "U").charAt(0).toUpperCase();
        authContainer.innerHTML = `
            <button type="button" class="profile-avatar-btn" onclick="openProfileSidebar()" title="View Profile & Orders">
                ${escapeHtml(initial)}
            </button>
        `;

        // Populate drawer contents if element exists
        const nameEl = document.getElementById("drawer-user-name");
        const emailEl = document.getElementById("drawer-user-email");
        const avatarEl = document.getElementById("drawer-user-avatar");
        if (nameEl) nameEl.innerText = appState.user.full_name || appState.user.username;
        if (emailEl) emailEl.innerText = appState.user.email || "customer@s4fashions.com";
        if (avatarEl) avatarEl.innerText = initial;
    } else {
        authContainer.innerHTML = `
            <a href="/login.html" class="nav-btn" style="border: 1px solid #e5e7eb; border-radius: 20px; padding: 6px 14px; font-size: 13px; font-weight: 600; text-decoration: none; color: #8e0d5d; background: #ffffff;">
                👤 Sign In
            </a>
        `;
    }
}

function logoutUser() {
    localStorage.removeItem("tc_token");
    localStorage.removeItem("tc_user");
    localStorage.removeItem("tc_login_time");
    appState.token = null;
    appState.user = null;
    closeProfileSidebar();
    window.location.href = "/";
}

// Cart Count Update across all pages and headers
function updateCartCounter() {
    // Always refresh cart state from localStorage first
    try {
        appState.cart = JSON.parse(localStorage.getItem("tc_cart") || "[]");
    } catch (e) {
        appState.cart = [];
    }

    const totalCount = appState.cart.reduce((acc, item) => acc + (parseInt(item.quantity, 10) || 1), 0);
    
    // Select all potential cart badge containers across all templates
    const selectors = ["#nav-cart-count", "#cart-count-badge", ".nav-cart-badge", ".cart-badge-count"];
    selectors.forEach(sel => {
        document.querySelectorAll(sel).forEach(el => {
            el.innerText = totalCount;
        });
    });
}

// Custom Popup Toast Notification System (Replaces Browser window.alert)
function showToastPopup(title, message, actionUrl = "/cart.html", actionText = "View Bag &rarr;") {
    let container = document.getElementById("s4-toast-container");
    if (!container) {
        container = document.createElement("div");
        container.id = "s4-toast-container";
        container.className = "s4-toast-container";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = "s4-toast-popup";
    toast.innerHTML = `
        <div class="toast-icon">🛍️</div>
        <div class="toast-message-box">
            <div class="toast-title">${escapeHtml(title)}</div>
            <div class="toast-body">${escapeHtml(message)}</div>
        </div>
        ${actionUrl ? `<a href="${actionUrl}" class="toast-action-btn">${actionText}</a>` : ''}
    `;

    container.appendChild(toast);

    // Trigger animation
    requestAnimationFrame(() => {
        toast.classList.add("show");
    });

    // Auto dismiss after 3.8s
    setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => toast.remove(), 350);
    }, 3800);
}

// Add Item to Cart
function addItemToCart(product, size, color, quantity = 1) {
    const existingIndex = appState.cart.findIndex(
        i => i.product_id === product.id && i.size === size && i.color === color
    );

    if (existingIndex > -1) {
        appState.cart[existingIndex].quantity += quantity;
    } else {
        appState.cart.push({
            product_id: product.id,
            title: product.title,
            brand: product.brand,
            price: product.price,
            original_price: product.original_price,
            size: size,
            color: color,
            quantity: quantity,
            image_url: product.image_url
        });
    }

    localStorage.setItem("tc_cart", JSON.stringify(appState.cart));
    updateCartCounter();
}

function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
