# Django E-commerce Application

# python manage.py runserver

A production-ready, full-stack e-commerce platform built with Django 4.2 LTS, Django REST Framework, Bootstrap, and AWS S3.

## 🏗️ Architecture

- **Backend**: Django 4.2 LTS + Django REST Framework
- **Database**: PostgreSQL (configurable, defaults to SQLite for development)
- **Frontend**: Django Templates + Bootstrap 5
- **Storage**: AWS S3 (images), Local filesystem (development)
- **Authentication**: Django built-in + Token-based API
- **Payment**: Dummy processor (extensible for Stripe/PayPal)

## 📦 Project Structure

```
ecommerce/
├── ecommerce/          # Main project config
├── users/              # User authentication and profiles
├── products/           # Products, categories, reviews
├── cart/               # Shopping cart system
├── orders/             # Orders and checkout
├── api/                # REST API (DRF)
├── core/               # Shared utilities
├── templates/          # Django templates
├── static/             # CSS, JS, images
├── media/              # User uploads (local)
└── manage.py           # Django CLI
```

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Navigate to project
cd k:\Django-Ecommerce

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Or on macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

```bash
# Copy example .env file
copy .env.example .env

# Edit .env with your settings (optional for development)
```

### 4. Database Setup

```bash
# Apply migrations
python manage.py migrate

# Create superuser for admin panel
python manage.py createsuperuser
```

### 5. Run Development Server

```bash
python manage.py runserver
```

Access the application at:
- Frontend: http://localhost:8000
- Admin Panel: http://localhost:8000/admin

## 📋 Features

### Phase 1: ✅ Project Setup
- Django project and 6 apps configured
- PostgreSQL/SQLite database ready
- AWS S3 integration configured
- Environment variables setup

### Phase 2: User Authentication (Coming)
- User registration and login
- Password reset with email
- User profile management
- Address management for shipping

### Phase 3: Products (Coming)
- Product catalog with categories
- Product listings with pagination
- Product detail pages
- Search and filtering

### Phase 4: Shopping Cart (Coming)
- Add/remove products
- Update quantities
- Session-based and database-persisted carts

### Phase 5: Checkout & Orders (Coming)
- Checkout flow
- Order creation
- Dummy payment processing
- Order history and tracking

### Phase 6: Wishlist & Reviews (Coming)
- Add to wishlist
- Product reviews and ratings

### Phase 7: REST API (Coming)
- Full DRF implementation
- Token authentication
- Pagination and filtering
- Rate limiting

### Phase 8: Frontend UI (Coming)
- Bootstrap responsive design
- Templates for all pages
- Form styling and validation

### Phase 9: AWS S3 Integration (Coming)
- Image upload and storage
- CDN configuration
- Static files on S3

### Phase 10: RAG Chatbot Integration ✅
- Semantic search using FAISS vector store
- Orchestration with LangChain & Google Gemini
- Real-time DB-to-Vector store synchronization signals
- Robust offline mock/fallback mode for local testing
- Detailed guide: [RAG_README.md](file:///k:/Django-Ecommerce/RAG_README.md)

## 🔌 REST API Endpoints

```
Authentication:
  POST   /api/v1/auth/register/      - Register new user
  POST   /api/v1/auth/login/         - User login

Products:
  GET    /api/v1/products/           - List products (paginated)
  GET    /api/v1/products/{id}/      - Product detail

Orders:
  POST   /api/v1/orders/             - Create order
  GET    /api/v1/orders/             - List user orders
  GET    /api/v1/orders/{id}/        - Order detail

Cart:
  GET    /api/v1/cart/               - View cart
  POST   /api/v1/cart/add/           - Add to cart
  DELETE /api/v1/cart/remove/{id}/   - Remove from cart
```

## 🔑 Environment Variables

See `.env.example` for all available configurations:

```env
DEBUG=True
SECRET_KEY=your-secret-key
DB_ENGINE=django.db.backends.postgresql
DB_NAME=ecommerce_db
USE_S3=False
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
```

## 📊 Admin Panel Features

- Product management with bulk actions
- Order tracking with status updates
- User management and analytics
- Category management
- Review moderation

## 🧪 Testing

```bash
# Run tests (when implemented)
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 🐳 Docker Support (Optional)

```bash
# Build image
docker build -t ecommerce .

# Run container
docker run -p 8000:8000 ecommerce
```

## 📱 Responsive Design

All templates are mobile-responsive using Bootstrap 5:
- Mobile-first design
- Tablet and desktop layouts
- Touch-friendly navigation

## 🔒 Security Features

- CSRF protection
- SQL injection prevention via ORM
- XSS protection with template escaping
- Password hashing with Django's authentication
- HTTPS enforced in production
- Secure cookie settings

## 🚢 Deployment

### Gunicorn (Production Server)

```bash
gunicorn ecommerce.wsgi --bind 0.0.0.0:8000
```

### Environment for Production

```env
DEBUG=False
SECRET_KEY=your-long-random-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
USE_S3=True
```

## 📚 Documentation

- Detailed API documentation: `/api/docs/` (when implemented)
- Model relationships: See individual app models.py
- Template tags and filters: See templates/

## 🤝 Contributing

1. Create a feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

## 📝 License

Licensed under MIT License. See LICENSE file for details.

## 🆘 Troubleshooting

### Migrations Issues
```bash
# Reset migrations (development only!)
python manage.py migrate users zero
python manage.py migrate
```

### Static Files Not Loading
```bash
python manage.py collectstatic --noinput
```

### Database Connection Error
Check `.env` settings and ensure PostgreSQL is running.

## 📞 Support

For issues and questions, check the documentation or create an issue in the repository.

---

Built with ❤️ using Django 4.2 LTS

 <!-- .\.venv\Scripts\Activate.ps1
 python manage.py runserver -->