const API_BASE = "/api/v1";

// State
let allProducts = [];
let cart = JSON.parse(localStorage.getItem("threadcraft_cart") || "[]");
let currentUser = JSON.parse(localStorage.getItem("threadcraft_user") || "null");
let authToken = localStorage.getItem("threadcraft_token") || null;
let currentCategory = "";

// Initialize App
document.addEventListener("DOMContentLoaded", () => {
    updateAuthUI();
    updateCartBadge();
    fetchProducts();
    setupEventListeners();
});

// Setup Events
function setupEventListeners() {
    // Search
    const searchInput = document.getElementById("search-input");
    let searchTimeout;
    searchInput.addEventListener("input", (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            fetchProducts();
        }, 300);
    });

    // Category Tabs
    document.querySelectorAll(".subnav-item").forEach(item => {
        item.addEventListener("click", (e) => {
            e.preventDefault();
            document.querySelectorAll(".subnav-item").forEach(i => i.classList.remove("active"));
            item.classList.add("active");
            currentCategory = item.getAttribute("data-category") || "";
            fetchProducts();
        });
    });

    // Filters
    document.getElementById("subcategory-filter").addEventListener("change", fetchProducts);
    document.getElementById("brand-filter").addEventListener("change", fetchProducts);
    document.getElementById("price-filter").addEventListener("change", fetchProducts);
    document.getElementById("btn-clear-filter").addEventListener("click", () => {
        document.getElementById("subcategory-filter").value = "";
        document.getElementById("brand-filter").value = "";
        document.getElementById("price-filter").value = "";
        document.getElementById("search-input").value = "";
        fetchProducts();
    });
}

// Fetch products from API
async function fetchProducts() {
    try {
        const search = document.getElementById("search-input").value.trim();
        const subcategory = document.getElementById("subcategory-filter").value;
        const brand = document.getElementById("brand-filter").value;
        const maxPrice = document.getElementById("price-filter").value;

        const params = new URLSearchParams();
        if (currentCategory) params.append("category", currentCategory);
        if (subcategory) params.append("subcategory", subcategory);
        if (brand) params.append("brand", brand);
        if (maxPrice) params.append("max_price", maxPrice);
        if (search) params.append("search", search);

        const res = await fetch(`${API_BASE}/products?${params.toString()}`);
        if (!res.ok) throw new Error("Failed to load catalog");
        const products = await res.json();
        allProducts = products;
        renderProducts(products);
    } catch (err) {
        console.error(err);
        document.getElementById("product-grid").innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #666;">
                <p>Failed to load products. Please check if the API server is running.</p>
            </div>
        `;
    }
}

// Render product cards
function renderProducts(products) {
    const grid = document.getElementById("product-grid");
    document.getElementById("products-count").innerText = `Showing ${products.length} clothing items`;

    if (products.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #666;">
                <p>No products found matching your filter criteria.</p>
            </div>
        `;
        return;
    }

    grid.innerHTML = products.map(p => {
        const discount = p.original_price && p.original_price > p.price
            ? Math.round(((p.original_price - p.price) / p.original_price) * 100)
            : 0;

        return `
            <div class="product-card">
                <img src="${p.image_url || 'https://via.placeholder.com/300x350'}" alt="${p.title}" class="product-img" loading="lazy">
                <div class="product-details">
                    <div class="product-brand">${escapeHtml(p.brand)}</div>
                    <div class="product-title" title="${escapeHtml(p.title)}">${escapeHtml(p.title)}</div>
                    <div class="product-rating">★ ${p.rating} <span style="font-size: 10px; color: #888;">(${p.rating_count})</span></div>
                    
                    <div class="product-price-row">
                        <span class="current-price">₹${p.price.toFixed(0)}</span>
                        ${p.original_price ? `<span class="orig-price">₹${p.original_price.toFixed(0)}</span>` : ''}
                        ${discount > 0 ? `<span class="discount-tag">${discount}% OFF</span>` : ''}
                    </div>

                    <div class="badge-row">
                        <span class="spec-badge">Sizes: ${escapeHtml(p.available_sizes)}</span>
                        <span class="spec-badge">${escapeHtml(p.material || 'Premium')}</span>
                    </div>

                    <button class="add-cart-btn" onclick="openProductModal(${p.id})">Add to Bag</button>
                </div>
            </div>
        `;
    }).join("");
}

// Open Product Modal to Select Size/Color
function openProductModal(productId) {
    const p = allProducts.find(item => item.id === productId);
    if (!p) return;

    const sizes = p.available_sizes.split(",").map(s => s.trim());
    const colors = p.available_colors.split(",").map(c => c.trim());

    const modalBody = document.getElementById("modal-body");
    modalBody.innerHTML = `
        <div style="display: flex; gap: 16px; margin-bottom: 16px;">
            <img src="${p.image_url}" style="width: 100px; height: 120px; object-fit: cover; border-radius: 6px;">
            <div>
                <h3 style="font-size: 16px; margin-bottom: 4px;">${escapeHtml(p.brand)}</h3>
                <p style="font-size: 13px; color: #666; margin-bottom: 8px;">${escapeHtml(p.title)}</p>
                <div style="font-size: 18px; font-weight: 700; color: #282c3f;">₹${p.price.toFixed(0)}</div>
            </div>
        </div>

        <div style="margin-bottom: 14px;">
            <label style="font-size: 13px; font-weight: 600; display: block; margin-bottom: 6px;">Select Size:</label>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                ${sizes.map((s, idx) => `
                    <label style="border: 1px solid #d4d5d9; padding: 6px 12px; border-radius: 4px; font-size: 13px; cursor: pointer;">
                        <input type="radio" name="modal_size" value="${s}" ${idx === 0 ? 'checked' : ''}> ${s}
                    </label>
                `).join("")}
            </div>
        </div>

        <div style="margin-bottom: 14px;">
            <label style="font-size: 13px; font-weight: 600; display: block; margin-bottom: 6px;">Select Color:</label>
            <select id="modal_color" style="width: 100%; padding: 8px; border-radius: 6px; border: 1px solid #d4d5d9;">
                ${colors.map(c => `<option value="${c}">${c}</option>`).join("")}
            </select>
        </div>

        <div style="margin-bottom: 18px;">
            <label style="font-size: 13px; font-weight: 600; display: block; margin-bottom: 6px;">Quantity:</label>
            <input type="number" id="modal_qty" value="1" min="1" max="10" style="width: 80px; padding: 6px 10px; border-radius: 6px; border: 1px solid #d4d5d9;">
        </div>

        <button class="add-cart-btn" onclick="addToCartConfirm(${p.id})">Confirm & Add to Bag</button>
    `;

    document.getElementById("generic-modal").classList.add("active");
}

function addToCartConfirm(productId) {
    const p = allProducts.find(item => item.id === productId);
    const sizeRadio = document.querySelector("input[name='modal_size']:checked");
    const color = document.getElementById("modal_color").value;
    const qty = parseInt(document.getElementById("modal_qty").value, 10);

    if (!sizeRadio || isNaN(qty) || qty <= 0) {
        alert("Please select valid size and quantity.");
        return;
    }

    cart.push({
        product_id: p.id,
        title: p.title,
        brand: p.brand,
        size: sizeRadio.value,
        color: color,
        quantity: qty,
        price: p.price,
        image_url: p.image_url
    });

    localStorage.setItem("threadcraft_cart", JSON.stringify(cart));
    updateCartBadge();
    closeModal();
    alert(`Added "${p.title}" to Bag!`);
}

function updateCartBadge() {
    const count = cart.reduce((acc, item) => acc + item.quantity, 0);
    document.getElementById("cart-count").innerText = count;
}

// Cart Drawer / Modal
function openCartModal() {
    const modalBody = document.getElementById("modal-body");
    if (cart.length === 0) {
        modalBody.innerHTML = `
            <div style="text-align: center; padding: 30px;">
                <p style="color: #666; margin-bottom: 16px;">Your Shopping Bag is empty.</p>
                <button class="add-cart-btn" onclick="closeModal()">Continue Shopping</button>
            </div>
        `;
    } else {
        const total = cart.reduce((acc, item) => acc + (item.price * item.quantity), 0);
        modalBody.innerHTML = `
            <h3 style="font-size: 18px; margin-bottom: 14px;">Shopping Bag (${cart.length} items)</h3>
            <div style="max-height: 250px; overflow-y: auto; margin-bottom: 16px; display: flex; flex-direction: column; gap: 10px;">
                ${cart.map((item, idx) => `
                    <div style="display: flex; gap: 12px; align-items: center; border-bottom: 1px solid #eee; padding-bottom: 8px;">
                        <img src="${item.image_url}" style="width: 50px; height: 60px; object-fit: cover; border-radius: 4px;">
                        <div style="flex: 1;">
                            <div style="font-weight: 600; font-size: 13px;">${escapeHtml(item.brand)} - ${escapeHtml(item.title)}</div>
                            <div style="font-size: 12px; color: #666;">Size: ${item.size} | Color: ${item.color} | Qty: ${item.quantity}</div>
                            <div style="font-weight: 700; font-size: 13px;">₹${(item.price * item.quantity).toFixed(0)}</div>
                        </div>
                        <button onclick="removeItemFromCart(${idx})" style="color: red; border: none; background: none; cursor: pointer; font-size: 16px;">&times;</button>
                    </div>
                `).join("")}
            </div>

            <div style="font-size: 16px; font-weight: 700; display: flex; justify-content: space-between; margin-bottom: 16px;">
                <span>Total Amount:</span>
                <span>₹${total.toFixed(0)}</span>
            </div>

            <div style="margin-bottom: 14px;">
                <label style="font-size: 13px; font-weight: 600; display: block; margin-bottom: 4px;">Delivery Address:</label>
                <textarea id="checkout-address" style="width: 100%; padding: 8px; border-radius: 6px; border: 1px solid #d4d5d9; font-size: 13px;" rows="2" placeholder="House no, Street, Landmark, City, Pincode"></textarea>
            </div>

            <div style="margin-bottom: 16px;">
                <label style="font-size: 13px; font-weight: 600; display: block; margin-bottom: 4px;">Phone Number:</label>
                <input type="text" id="checkout-phone" style="width: 100%; padding: 8px; border-radius: 6px; border: 1px solid #d4d5d9; font-size: 13px;" placeholder="+91 9876543210">
            </div>

            <button class="add-cart-btn" onclick="executeCheckout()">Place Order (Cash on Delivery)</button>
        `;
    }

    document.getElementById("generic-modal").classList.add("active");
}

function removeItemFromCart(index) {
    cart.splice(index, 1);
    localStorage.setItem("threadcraft_cart", JSON.stringify(cart));
    updateCartBadge();
    openCartModal();
}

// Checkout Execution
async function executeCheckout() {
    if (!authToken) {
        alert("Please login first to place an order.");
        openAuthModal();
        return;
    }

    const address = document.getElementById("checkout-address").value.trim();
    const phone = document.getElementById("checkout-phone").value.trim();

    if (!address || !phone) {
        alert("Please provide both shipping address and phone number.");
        return;
    }

    const payload = {
        items: cart.map(i => ({
            product_id: i.product_id,
            size: i.size,
            color: i.color,
            quantity: i.quantity
        })),
        shipping_address: address,
        phone_number: phone
    };

    try {
        const res = await fetch(`${API_BASE}/orders/checkout`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${authToken}`
            },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (!res.ok) {
            alert(`Order Failed: ${data.message || data.error || "Validation error"}`);
            return;
        }

        cart = [];
        localStorage.removeItem("threadcraft_cart");
        updateCartBadge();
        closeModal();
        alert(`🎉 Order Placed Successfully! Order ID: #${data.id}\nTotal: ₹${data.total_amount}`);
    } catch (err) {
        alert("Network error occurred during checkout.");
    }
}

// Auth Modal
function openAuthModal() {
    const modalBody = document.getElementById("modal-body");
    modalBody.innerHTML = `
        <h3 style="font-size: 18px; margin-bottom: 14px;">Customer / Staff Login</h3>
        <p style="font-size: 12px; color: #666; margin-bottom: 12px;">Demo accounts: <b>alice_customer</b> / <b>AlicePassword123!</b> or <b>admin_user</b> / <b>Admin@ThreadCraft2026!</b></p>
        
        <div style="margin-bottom: 12px;">
            <label style="font-size: 13px; font-weight: 600; display: block; margin-bottom: 4px;">Username:</label>
            <input type="text" id="login-username" style="width: 100%; padding: 8px; border-radius: 6px; border: 1px solid #d4d5d9;" value="alice_customer">
        </div>

        <div style="margin-bottom: 16px;">
            <label style="font-size: 13px; font-weight: 600; display: block; margin-bottom: 4px;">Password:</label>
            <input type="password" id="login-password" style="width: 100%; padding: 8px; border-radius: 6px; border: 1px solid #d4d5d9;" value="AlicePassword123!">
        </div>

        <button class="add-cart-btn" onclick="executeLogin()">Login</button>
    `;
    document.getElementById("generic-modal").classList.add("active");
}

async function executeLogin() {
    const u = document.getElementById("login-username").value.trim();
    const p = document.getElementById("login-password").value;

    try {
        const res = await fetch(`${API_BASE}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: u, password: p })
        });
        const data = await res.json();
        if (!res.ok) {
            alert(data.message || data.error || "Login failed");
            return;
        }

        authToken = data.access_token;
        currentUser = data.user;
        localStorage.setItem("threadcraft_token", authToken);
        localStorage.setItem("threadcraft_user", JSON.stringify(currentUser));
        updateAuthUI();
        closeModal();
        alert(`Welcome back, ${currentUser.full_name || currentUser.username}! (Role: ${currentUser.role})`);
    } catch (err) {
        alert("Failed to connect to authentication server.");
    }
}

function updateAuthUI() {
    const authBtn = document.getElementById("auth-btn");
    if (currentUser) {
        authBtn.innerHTML = `👤 ${escapeHtml(currentUser.username)} <span style="font-size: 10px; color: #888;">(${currentUser.role})</span>`;
        authBtn.onclick = () => {
            if (confirm(`Logged in as ${currentUser.username}. Do you want to logout?`)) {
                localStorage.removeItem("threadcraft_token");
                localStorage.removeItem("threadcraft_user");
                authToken = null;
                currentUser = null;
                updateAuthUI();
            }
        };
    } else {
        authBtn.innerHTML = `👤 Login`;
        authBtn.onclick = openAuthModal;
    }
}

// View My Orders
async function openOrdersModal() {
    if (!authToken) {
        alert("Please login to view your order history.");
        openAuthModal();
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/orders`, {
            headers: { "Authorization": `Bearer ${authToken}` }
        });
        const orders = await res.json();
        const modalBody = document.getElementById("modal-body");

        if (!res.ok || orders.length === 0) {
            modalBody.innerHTML = `
                <div style="text-align: center; padding: 30px;">
                    <p style="color: #666;">No orders placed yet.</p>
                </div>
            `;
        } else {
            modalBody.innerHTML = `
                <h3 style="font-size: 18px; margin-bottom: 14px;">My Orders (${orders.length})</h3>
                <div style="display: flex; flex-direction: column; gap: 12px; max-height: 400px; overflow-y: auto;">
                    ${orders.map(o => `
                        <div style="border: 1px solid #eaeaec; border-radius: 8px; padding: 12px; background: #fafafa;">
                            <div style="display: flex; justify-content: space-between; font-weight: 700; font-size: 14px; margin-bottom: 6px;">
                                <span>Order #${o.id}</span>
                                <span style="color: var(--primary);">₹${o.total_amount.toFixed(0)}</span>
                            </div>
                            <div style="font-size: 12px; color: #666; margin-bottom: 6px;">Status: <b>${o.status.toUpperCase()}</b> | Placed: ${new Date(o.created_at).toLocaleDateString()}</div>
                            <div style="font-size: 12px; color: #444;">Items: ${o.items.map(i => `${i.product_title} (${i.size}, ${i.quantity}x)`).join(", ")}</div>
                        </div>
                    `).join("")}
                </div>
            `;
        }

        document.getElementById("generic-modal").classList.add("active");
    } catch (err) {
        alert("Failed to load order history.");
    }
}

function closeModal() {
    document.getElementById("generic-modal").classList.remove("active");
}

function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
