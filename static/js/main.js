/* E-Commerce Bootstrap Main JavaScript */

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Add to cart confirmation
    const addToCartButtons = document.querySelectorAll('[data-action="add-to-cart"]');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            addToCart(productId);
        });
    });

    // Quantity selector
    const quantityInputs = document.querySelectorAll('[data-action="quantity"]');
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            const cartItemId = this.dataset.cartItemId;
            const quantity = this.value;
            updateQuantity(cartItemId, quantity);
        });
    });
});

/**
 * Add item to cart
 */
function addToCart(productId) {
    fetch(`/cart/add/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: 1
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage('Product added to cart!', 'success');
            updateCartCount();
        } else {
            showMessage(data.message || 'Error adding to cart', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('Error adding to cart', 'danger');
    });
}

/**
 * Update cart item quantity
 */
function updateQuantity(cartItemId, quantity) {
    fetch(`/cart/update/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            cart_item_id: cartItemId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            showMessage(data.message || 'Error updating cart', 'danger');
        }
    });
}

/**
 * Show message alert
 */
function showMessage(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
          
    const container = document.querySelector('main') || document.body;
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alertDiv);
        bsAlert.close();
    }, 5000);
}

/**
 * Get CSRF token from cookies
 */
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

/**
 * Update cart count in navbar
 */
function updateCartCount() {
    fetch('/cart/count/')
        .then(response => response.json())
        .then(data => {
            const cartBadge = document.querySelector('[data-cart-count]');
            if (cartBadge) {
                cartBadge.textContent = data.count;
            }
        });
}
