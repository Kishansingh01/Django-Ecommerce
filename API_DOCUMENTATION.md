# Django E-Commerce API Documentation

## Base URL
```
http://localhost:8000/api/
```

## Authentication
All authenticated endpoints require a token in the Authorization header:
```
Authorization: Token your-token-here
```

To get a token:
```
POST /api/auth/token/
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

## API Endpoints

### Users
- `GET /api/users/` - List all users (paginated)
- `GET /api/users/{id}/` - Get user by ID
- `GET /api/users/me/` - Get current user profile (requires authentication)

### Addresses
- `GET /api/addresses/` - List your addresses (requires authentication)
- `POST /api/addresses/` - Create new address (requires authentication)
- `GET /api/addresses/{id}/` - Get address by ID (requires authentication)
- `PUT /api/addresses/{id}/` - Update address (requires authentication)
- `DELETE /api/addresses/{id}/` - Delete address (requires authentication)

### Categories
- `GET /api/categories/` - List all product categories
- `GET /api/categories/{id}/` - Get category details

### Products
- `GET /api/products/` - List all active products (paginated, filterable, searchable)
- `GET /api/products/{id}/` - Get product details with images and reviews
- `GET /api/products/featured/` - Get featured products
- `GET /api/products/?search=query` - Search products
- `GET /api/products/?category={id}` - Filter by category
- `GET /api/products/?min_price=100&max_price=500` - Filter by price range
- `GET /api/products/?ordering=price` - Sort by price (or `-price`, `created_at`, `-created_at`, `name`)

### Reviews
- `GET /api/reviews/?product={product_id}` - List reviews for a product
- `POST /api/reviews/` - Create review for a product (requires authentication)
  ```json
  {
      "product_id": 1,
      "rating": 5,
      "title": "Great product!",
      "comment": "Very satisfied with this purchase."
  }
  ```
- `PUT /api/reviews/{id}/` - Update your review (requires authentication)
- `DELETE /api/reviews/{id}/` - Delete your review (requires authentication)

### Wishlist
- `GET /api/wishlist/` - Get your wishlist (requires authentication)
- `POST /api/wishlist/add/` - Add product to wishlist (requires authentication)
  ```json
  {
      "product_id": 1
  }
  ```
- `POST /api/wishlist/remove/` - Remove product from wishlist (requires authentication)
  ```json
  {
      "product_id": 1
  }
  ```

### Shopping Cart
- `GET /api/cart/` - Get your cart (requires authentication)
- `POST /api/cart/add/` - Add product to cart (requires authentication)
  ```json
  {
      "product_id": 1,
      "quantity": 2
  }
  ```
- `POST /api/cart/update-item/` - Update item quantity in cart (requires authentication)
  ```json
  {
      "product_id": 1,
      "quantity": 3
  }
  ```
- `POST /api/cart/remove/` - Remove product from cart (requires authentication)
  ```json
  {
      "product_id": 1
  }
  ```
- `POST /api/cart/clear/` - Clear entire cart (requires authentication)

### Orders
- `GET /api/orders/` - List your orders (paginated, requires authentication)
- `GET /api/orders/{id}/` - Get order details (requires authentication)
- `POST /api/orders/{id}/cancel/` - Cancel an order (requires authentication)

## Response Format

### Success Response
```json
{
    "id": 1,
    "name": "Product Name",
    "price": "99.99",
    "description": "Product description",
    ...
}
```

### Error Response
```json
{
    "error": "Error message",
    "detail": "Detailed error information"
}
```

### Paginated Response
```json
{
    "count": 100,
    "next": "http://localhost:8000/api/products/?page=2",
    "previous": null,
    "results": [
        { ... },
        { ... }
    ]
}
```

## Status Codes
- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `204 No Content` - Request successful, no content to return
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Examples

### Get Product Details
```bash
curl http://localhost:8000/api/products/1/
```

### Search Products
```bash
curl "http://localhost:8000/api/products/?search=laptop"
```

### Filter Products by Price
```bash
curl "http://localhost:8000/api/products/?min_price=100&max_price=500"
```

### Add Product to Cart
```bash
curl -X POST http://localhost:8000/api/cart/add/ \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 2}'
```

### Get User Orders
```bash
curl http://localhost:8000/api/orders/ \
  -H "Authorization: Token your-token"
```

## Pagination
Default page size: 12 items per page

To change page:
```
/api/products/?page=2
```

To customize page size:
```
/api/products/?page_size=20&page=1
```

## Rate Limiting
API endpoints are rate-limited:
- Anonymous users: 100 requests per hour
- Authenticated users: 1000 requests per hour

## CORS
CORS is enabled for all origins. API can be accessed from frontend applications.
