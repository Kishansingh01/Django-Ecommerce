# Deployment Guide

## Production Checklist

### 1. Environment Configuration

Update `.env` for production:

```env
DEBUG=False
SECRET_KEY=generate-long-random-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=ecommerce_prod
DB_USER=postgres
DB_PASSWORD=strong-password
DB_HOST=your-db-host.rds.amazonaws.com
DB_PORT=5432

# AWS S3
USE_S3=True
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=ecommerce-prod-bucket
AWS_S3_REGION_NAME=us-east-1

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

### 2. Database Setup

#### PostgreSQL on AWS RDS

```bash
# Create RDS instance via AWS Console or CLI
aws rds create-db-instance \
  --db-instance-identifier ecommerce-prod \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username postgres \
  --master-user-password "your-strong-password" \
  --allocated-storage 20

# Connect and create database
psql -U postgres -h ecommerce-prod.xxx.us-east-1.rds.amazonaws.com
CREATE DATABASE ecommerce_prod;
```

Link application to RDS in Django settings (already configured).

### 3. S3 Bucket Configuration

```bash
# Create S3 bucket
aws s3api create-bucket \
  --bucket ecommerce-prod-bucket \
  --region us-east-1

# Configure bucket policy for public read access (optional)
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::ecommerce-prod-bucket/*"
        }
    ]
}

# Enable CloudFront CDN for faster delivery
# Configure distribution in AWS CloudFront console
```

### 4. Django Migrations

```bash
# Run migrations on production
python manage.py migrate --noinput

# Collect static files to S3
python manage.py collectstatic --noinput
```

### 5. WSGI Server (Gunicorn)

```bash
# Install Gunicorn (already in requirements.txt)
pip install gunicorn

# Run production server
gunicorn ecommerce.wsgi \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --worker-class sync \
  --timeout 60 \
  --access-logfile - \
  --error-logfile -

# Or use with systemd service (see systemd-setup below)
```

### 6. Systemd Service (Linux)

Create `/etc/systemd/system/ecommerce.service`:

```ini
[Unit]
Description=Django E-commerce Application
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/home/ubuntu/Django-Ecommerce
ExecStart=/home/ubuntu/Django-Ecommerce/venv/bin/gunicorn \
  ecommerce.wsgi \
  --bind 127.0.0.1:8000 \
  --workers 4 \
  --timeout 60
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ecommerce
sudo systemctl start ecommerce
sudo systemctl status ecommerce
```

### 7. Nginx Configuration

Create `/etc/nginx/sites-available/ecommerce`:

```nginx
upstream ecommerce {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL certificates (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    client_max_body_size 20M;

    location / {
        proxy_pass http://ecommerce;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/ubuntu/Django-Ecommerce/staticfiles/;
    }

    location /media/ {
        alias /home/ubuntu/Django-Ecommerce/media/;
    }
}
```

Enable and reload:

```bash
sudo ln -s /etc/nginx/sites-available/ecommerce /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 8. SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly \
  --standalone \
  --email your-email@example.com \
  -d yourdomain.com \
  -d www.yourdomain.com

# Auto-renewal (cron job)
sudo crontab -e
# Add: 0 3 * * * certbot renew --quiet
```

### 9. Docker Deployment (Optional)

#### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run migrations and start Gunicorn
CMD ["sh", "-c", "python manage.py migrate && gunicorn ecommerce.wsgi --bind 0.0.0.0:8000"]

EXPOSE 8000
```

#### Docker Compose

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ecommerce_prod
      POSTGRES_PASSWORD: strong-password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  web:
    build: .
    command: gunicorn ecommerce.wsgi --bind 0.0.0.0:8000
    ports:
      - "8000:8000"
    environment:
      DEBUG: 'False'
      DB_NAME: ecommerce_prod
      DB_USER: postgres
      DB_PASSWORD: strong-password
      DB_HOST: db
      DB_PORT: 5432
    depends_on:
      - db

volumes:
  postgres_data:
```

Run:

```bash
docker-compose build
docker-compose up -d
```

### 10. Monitoring and Logging

#### Sentry (Error Tracking)

```bash
pip install sentry-sdk
```

Add to `settings.py`:

```python
import sentry_sdk
sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=0.1,
    environment="production"
)
```

#### Application Logs

Configure in `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/ecommerce/django.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### 11. Backup Strategy

#### Database Backups

```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/backups/postgresql"
DB_NAME="ecommerce_prod"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

pg_dump -U postgres -h db-host $DB_NAME | gzip > $BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz

# Keep last 7 days
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +7 -delete
```

Add to crontab:

```bash
0 2 * * * /home/ubuntu/backup.sh
```

#### S3 Backups

```bash
# Backup media files to S3
aws s3 sync /home/ubuntu/Django-Ecommerce/media s3://ecommerce-prod-bucket/backups/media/ --delete
```

### 12. Performance Optimization

- Enable Redis caching
- Use CDN for static files
- Database connection pooling
- Enable GZIP compression in Nginx
- Optimize database queries (use select_related, prefetch_related)

### 13. Health Monitoring

Create health check endpoint in `core/views.py`:

```python
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'healthy'})
```

Add to URLs:

```python
path('health/', health_check)
```

Monitor with:

```bash
curl https://yourdomain.com/health/
```

## Troubleshooting

- **Static files not loading**: Run `collectstatic` again
- **Database connection errors**: Check RDS security groups
- **S3 permission errors**: Verify IAM credentials
- **Slow queries**: Check database indexes and enable query logging

## Scaling

- **Database**: Use RDS Multi-AZ for high availability
- **Application**: Use load balancer with multiple app servers
- **Media storage**: CloudFront CDN for faster delivery
- **Cache**: Redis for session and query caching
