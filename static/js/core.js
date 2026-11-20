// ThreadCraft Apparel - Core Client Engine
const API_BASE = "/api/v1";

// User-Scoped Cart Helpers
function getCartKey() {
    try {
        const u = JSON.parse(localStorage.getItem("tc_user") || "null");
        if (u && (u.id || u.username)) {
            return "tc_cart_u_" + (u.id || u.username);
        }
    } catch (e) {}
    return "tc_cart_guest";
}

function getStoredCart() {
    try {
        const key = getCartKey();
        const stored = localStorage.getItem(key);
        if (stored) {
            const parsed = JSON.parse(stored);
            if (Array.isArray(parsed)) return parsed;
        }
    } catch (e) {}
    return [];
}

function saveStoredCart(items) {
    appState.cart = Array.isArray(items) ? items : [];
    try {
        const key = getCartKey();
        localStorage.setItem(key, JSON.stringify(appState.cart));
        // Keep active session cart in sync
        localStorage.setItem("tc_cart", JSON.stringify(appState.cart));
    } catch (e) {}
    updateCartCounter();
}

function clearUserCart() {
    appState.cart = [];
    try {
        localStorage.removeItem(getCartKey());
        localStorage.removeItem("tc_cart");
        localStorage.removeItem("tc_cart_guest");
    } catch (e) {}
    updateCartCounter();
}

// State Management
let appState = {
    products: [],
    filteredProducts: [],
    cart: getStoredCart(),
    user: JSON.parse(localStorage.getItem("tc_user") || "null"),
    token: localStorage.getItem("tc_token") || null,
    selectedCategory: "",
    selectedSubcategory: "",
    selectedBrand: "",
    maxPrice: null,
    minRating: null,
    searchQuery: ""
};

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
    localStorage.removeItem("tc_cart");
    localStorage.removeItem("tc_cart_guest");
    appState.token = null;
    appState.user = null;
    appState.cart = [];
    updateCartCounter();
    closeProfileSidebar();
    window.location.href = "/";
}

// Initialize
function initApp() {
    syncAuthHeader();
    updateCartCounter();
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initApp);
} else {
    initApp();
}

// Window load listener to ensure late-mounted elements get updated
window.addEventListener("load", () => {
    updateCartCounter();
});

// Storage event listener to sync cart counter across multi-tabs in real-time
window.addEventListener("storage", (e) => {
    if (e.key === "tc_cart") {
        updateCartCounter();
    }
    if (e.key === "tc_user" || e.key === "tc_token") {
        try {
            appState.user = JSON.parse(localStorage.getItem("tc_user") || "null");
            appState.token = localStorage.getItem("tc_token") || null;
            syncAuthHeader();
        } catch (err) {}
    }
});

// Cart Count Update across all pages and headers
function updateCartCounter() {
    let items = getStoredCart();
    appState.cart = items;

    const totalCount = items.reduce((acc, item) => acc + (parseInt(item.quantity, 10) || 1), 0);
    
    // Select all potential cart badge containers across all templates
    const selectors = ["#nav-cart-count", "#cart-count-badge", ".nav-cart-badge", ".cart-badge-count", "#header-cart-badge"];
    selectors.forEach(sel => {
        document.querySelectorAll(sel).forEach(el => {
            el.innerText = totalCount;
        });
    });
    return totalCount;
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
    let currentCart = getStoredCart();
    const existingIndex = currentCart.findIndex(
        i => i.product_id === product.id && i.size === size && i.color === color
    );

    if (existingIndex > -1) {
        currentCart[existingIndex].quantity += quantity;
    } else {
        currentCart.push({
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

    saveStoredCart(currentCart);
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

function colorNameToCss(name) {
    const map = {
        "black": "#1a1a1a", "white": "#f8f8f8", "navy": "#001f5b",
        "charcoal": "#36454F", "grey": "#808080", "gray": "#808080",
        "red": "#cc2222", "maroon": "#800020", "burgundy": "#800020",
        "wine": "#722F37", "blue": "#1E5BB0", "skyblue": "#87CEEB",
        "green": "#2E7D32", "olive": "#708238", "khaki": "#C3B091",
        "yellow": "#FDD835", "orange": "#E65100", "pink": "#E91E8C",
        "purple": "#6A1B9A", "lavender": "#967BB6", "brown": "#795548",
        "beige": "#F5F0DC", "cream": "#FFFDD0", "offwhite": "#FAF9F6",
        "mustard": "#FFDB58", "coral": "#FF6B6B", "teal": "#008080",
        "indigo": "#3F51B5", "gold": "#FFD700", "silver": "#C0C0C0",
        "rust": "#B7410E", "peach": "#FFDAB9", "mint": "#98FF98",
        "aqua": "#00FFFF", "cyan": "#00BCD4", "magenta": "#8E0D5D",
        "emerald": "#50C878", "cobalt": "#0047AB", "ivory": "#FFFFF0",
        "taupe": "#483C32", "tan": "#D2B48C", "denim": "#1560BD",
        "champagne": "#F7E7CE", "blush": "#FFB6C1",
    };
    const key = (name || "").toLowerCase().replace(/\s+/g, "");
    return map[key] || `hsl(${Math.abs((name || "").split("").reduce((a, c) => a + c.charCodeAt(0), 0)) % 360}, 55%, 50%)`;
}
