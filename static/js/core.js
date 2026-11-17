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
    handleSplashScreen();
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

// Authentication UI Sync
function syncAuthHeader() {
    const authContainer = document.getElementById("header-auth-slot");
    if (!authContainer) return;

    if (appState.user && appState.token) {
        authContainer.innerHTML = `
            <div style="position: relative; display: inline-block;">
                <button class="header-nav-link" onclick="toggleUserDropdown()" style="color: #ffffff;">
                    <span>${escapeHtml(appState.user.username)}</span>
                    <span style="font-size: 11px; background: rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 2px;">
                        ${appState.user.role.toUpperCase()}
                    </span>
                </button>
                <div id="user-dropdown" style="display: none; position: absolute; right: 0; top: 100%; background: #ffffff; color: #212121; box-shadow: 0 4px 16px rgba(0,0,0,0.15); border-radius: 2px; width: 160px; z-index: 1000; margin-top: 8px;">
                    <a href="/orders.html" style="display: block; padding: 10px 14px; font-size: 13px; text-decoration: none; color: #212121; border-bottom: 1px solid #f0f0f0;">My Orders</a>
                    ${appState.user.role === 'admin' ? '<a href="/admin.html" style="display: block; padding: 10px 14px; font-size: 13px; text-decoration: none; color: #2874f0; border-bottom: 1px solid #f0f0f0;">Admin Portal</a>' : ''}
                    <button onclick="logoutUser()" style="width: 100%; text-align: left; padding: 10px 14px; font-size: 13px; border: none; background: none; cursor: pointer; color: #d32f2f;">Logout</button>
                </div>
            </div>
        `;
    } else {
        authContainer.innerHTML = `
            <a href="/login.html" class="login-btn-header">Login</a>
        `;
    }
}

function toggleUserDropdown() {
    const dd = document.getElementById("user-dropdown");
    if (dd) {
        dd.style.display = dd.style.display === "block" ? "none" : "block";
    }
}

// Global click to close dropdown
document.addEventListener("click", (e) => {
    const dd = document.getElementById("user-dropdown");
    if (dd && !e.target.closest("#header-auth-slot")) {
        dd.style.display = "none";
    }
});

function logoutUser() {
    localStorage.removeItem("tc_token");
    localStorage.removeItem("tc_user");
    appState.token = null;
    appState.user = null;
    syncAuthHeader();
    window.location.href = "/";
}

// Cart Count Update
function updateCartCounter() {
    const countEl = document.getElementById("cart-count-badge");
    if (!countEl) return;
    const totalCount = appState.cart.reduce((acc, item) => acc + item.quantity, 0);
    countEl.innerText = totalCount;
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
