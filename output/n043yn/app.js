/* filename: app.js */
document.addEventListener('DOMContentLoaded', () => {
    // State
    let products = [];
    let cart = [];

    // DOM Elements
    const productGrid = document.getElementById('product-grid');
    const cartBtn = document.getElementById('cart-btn');
    const closeCartBtn = document.getElementById('close-cart');
    const cartSidebar = document.getElementById('cart-sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    const cartItemsContainer = document.getElementById('cart-items');
    const cartCount = document.getElementById('cart-count');
    const cartTotal = document.getElementById('cart-total');
    const checkoutBtn = document.getElementById('checkout-btn');
    const toast = document.getElementById('toast');

    // Fetch Products
    async function fetchProducts() {
        try {
            const response = await fetch('/api/products');
            products = await response.json();
            renderProducts();
        } catch (error) {
            console.error('Error fetching products:', error);
            productGrid.innerHTML = '<p style="color:red; text-align:center; grid-column:1/-1;">Failed to load products.</p>';
        }
    }

    // Render Products
    function renderProducts() {
        productGrid.innerHTML = '';
        products.forEach(product => {
            const card = document.createElement('div');
            card.className = 'product-card';
            card.innerHTML = `
                <img src="${product.image_url}" alt="${product.name}" class="product-img">
                <div class="product-info">
                    <h3 class="product-title">${product.name}</h3>
                    <p class="product-desc">${product.description}</p>
                    <div class="product-footer">
                        <span class="product-price">$${product.price.toFixed(2)}</span>
                        <button class="add-to-cart-btn" data-id="${product.id}">Add to Cart</button>
                    </div>
                </div>
            `;
            productGrid.appendChild(card);
        });

        // Attach event listeners to Add to Cart buttons
        document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = parseInt(e.target.getAttribute('data-id'));
                addToCart(id);
            });
        });
    }

    // Cart Functions
    function addToCart(id) {
        const product = products.find(p => p.id === id);
        const existingItem = cart.find(item => item.product_id === id);

        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            cart.push({
                product_id: product.id,
                name: product.name,
                price: product.price,
                image_url: product.image_url,
                quantity: 1
            });
        }
        
        updateCartUI();
        showToast(`Added ${product.name} to cart`);
    }

    function updateQuantity(id, change) {
        const item = cart.find(i => i.product_id === id);
        if (item) {
            item.quantity += change;
            if (item.quantity <= 0) {
                cart = cart.filter(i => i.product_id !== id);
            }
            updateCartUI();
        }
    }

    function updateCartUI() {
        // Update count
        const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
        cartCount.textContent = totalItems;

        // Render items
        cartItemsContainer.innerHTML = '';
        if (cart.length === 0) {
            cartItemsContainer.innerHTML = '<p style="text-align:center; color:#6b7280; margin-top: 2rem;">Your cart is empty.</p>';
        } else {
            cart.forEach(item => {
                const div = document.createElement('div');
                div.className = 'cart-item';
                div.innerHTML = `
                    <img src="${item.image_url}" alt="${item.name}" class="cart-item-img">
                    <div class="cart-item-info">
                        <div class="cart-item-title">${item.name}</div>
                        <div class="cart-item-price">$${item.price.toFixed(2)}</div>
                        <div class="cart-item-controls">
                            <button class="qty-btn minus" data-id="${item.product_id}">-</button>
                            <span>${item.quantity}</span>
                            <button class="qty-btn plus" data-id="${item.product_id}">+</button>
                        </div>
                    </div>
                    <div style="font-weight: 600;">$${(item.price * item.quantity).toFixed(2)}</div>
                `;
                cartItemsContainer.appendChild(div);
            });
        }

        // Attach listeners for +/- buttons
        document.querySelectorAll('.qty-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = parseInt(e.target.getAttribute('data-id'));
                const isPlus = e.target.classList.contains('plus');
                updateQuantity(id, isPlus ? 1 : -1);
            });
        });

        // Update Total
        const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        cartTotal.textContent = total.toFixed(2);
    }

    // Checkout
    async function handleCheckout() {
        if (cart.length === 0) {
            showToast("Your cart is empty!");
            return;
        }

        checkoutBtn.textContent = 'Processing...';
        checkoutBtn.disabled = true;

        const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        const payload = {
            items: cart.map(i => ({ product_id: i.product_id, quantity: i.quantity })),
            total: total
        };

        try {
            const response = await fetch('/api/checkout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await response.json();
            
            cart = [];
            updateCartUI();
            toggleCart();
            showToast(`Success! Order #${data.order_id} placed.`);
        } catch (error) {
            console.error('Checkout error:', error);
            showToast("Checkout failed. Please try again.");
        } finally {
            checkoutBtn.textContent = 'Proceed to Checkout';
            checkoutBtn.disabled = false;
        }
    }

    // UI Utilities
    function toggleCart() {
        cartSidebar.classList.toggle('open');
        overlay.classList.toggle('show');
    }

    function showToast(message) {
        toast.textContent = message;
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }

    // Event Listeners
    cartBtn.addEventListener('click', toggleCart);
    closeCartBtn.addEventListener('click', toggleCart);
    overlay.addEventListener('click', toggleCart);
    checkoutBtn.addEventListener('click', handleCheckout);

    // Init
    fetchProducts();
    updateCartUI();
});
