# AWS S3 Configuration Guide

## Overview

This application is configured to use AWS S3 for storing media files (product images, user profile pictures). Storage can be toggled between local filesystem (development) and S3 (production) via environment variables.

## Setup Steps

### 1. Create AWS S3 Bucket

#### Via AWS Console
1. Go to S3 Management Console
2. Click "Create Bucket"
3. Enter bucket name: `ecommerce-prod-bucket` (must be globally unique)
4. Select region: `us-east-1`
5. Uncheck "Block Public Access" (if you want public images)
6. Click Create

#### Via AWS CLI
```bash
aws s3api create-bucket \
  --bucket ecommerce-prod-bucket \
  --region us-east-1
```

### 2. Create IAM User for Application

1. Go to IAM Management Console
2. Click "Users" > "Create User"
3. Username: `ecommerce-app`
4. Create access key for programmatic access
5. Save `Access Key ID` and `Secret Access Key`

### 3. Attach S3 Policy to IAM User

Create inline policy with the following:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::ecommerce-prod-bucket/*",
                "arn:aws:s3:::ecommerce-prod-bucket"
            ]
        }
    ]
}
```

### 4. Configure Application

Update `.env` file:

```env
# Enable S3 storage
USE_S3=True

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_STORAGE_BUCKET_NAME=ecommerce-prod-bucket
AWS_S3_REGION_NAME=us-east-1
AWS_S3_CUSTOM_DOMAIN=ecommerce-prod-bucket.s3.amazonaws.com

# Optional: Use CloudFront CDN
USE_CLOUDFRONT=False
CLOUDFRONT_DOMAIN=d123456789.cloudfront.net
```

### 5. Migrate Existing Media (Optional)

If migrating from local storage:

```bash
# Sync local media to S3
aws s3 sync media/ s3://ecommerce-prod-bucket/media/

# Remove local files if migration complete
rm -rf media/
```

### 6. Upload Initial Media

```bash
# Upload product images
aws s3 cp path/to/images/ s3://ecommerce-prod-bucket/media/products/ --recursive

# Upload user profile pictures
aws s3 cp path/to/profiles/ s3://ecommerce-prod-bucket/media/profile_pictures/ --recursive
```

## Static Files on S3 (Optional)

To also serve static files from S3:

### Update settings.py

```python
if USE_S3:
    # Static files
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    
    # Media files
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
    DEFAULT_FILE_STORAGE = 'core.storage.MediaRootS3Boto3Storage'
else:
    # Local storage (development)
    STATIC_URL = '/static/'
    MEDIA_URL = '/media/'
```

### Collect Static Files to S3

```bash
python manage.py collectstatic --noinput
```

## CloudFront CDN Configuration (Recommended)

### Create CloudFront Distribution

1. Go to CloudFront Management Console
2. Click "Create Distribution"
3. Choose S3 bucket as origin: `ecommerce-prod-bucket.s3.amazonaws.com`
4. Set Cache Behavior:
   - Viewer Protocol Policy: Redirect HTTP to HTTPS
   - Allowed HTTP Methods: GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE
   - Cache Policy: CachingOptimized
5. Create Distribution and wait for deployment (~15 minutes)

### Update Application

Once CloudFront is deployed:

```env
USE_CLOUDFRONT=True
CLOUDFRONT_DOMAIN=d123456789.cloudfront.net
```

Update settings.py:

```python
if USE_S3:
    if USE_CLOUDFRONT:
        STATIC_URL = f'https://{CLOUDFRONT_DOMAIN}/static/'
        MEDIA_URL = f'https://{CLOUDFRONT_DOMAIN}/media/'
    else:
        STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
        MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
```

## Bucket Policies

### Public Read Access (for images)

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::ecommerce-prod-bucket/media/*"
        }
    ]
}
```

### Restrict to CloudFront

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "CloudFrontAccess",
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudfront.amazonaws.com"
            },
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::ecommerce-prod-bucket/*",
            "Condition": {
                "StringEquals": {
                    "AWS:SourceArn": "arn:aws:cloudfront::ACCOUNT-ID:distribution/DISTRIBUTION-ID"
                }
            }
        }
    ]
}
```

## Image Optimization

### Install Pillow (already in requirements.txt)

```bash
pip install Pillow
```

### Create Image Processing Utility

Create `core/image_utils.py`:

```python
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

def resize_image(image, max_width=1200, max_height=1200, quality=85):
    """Resize image to fit within max dimensions while maintaining aspect ratio."""
    img = Image.open(image)
    
    # Convert RGBA to RGB if necessary
    if img.mode in ('RGBA', 'LA', 'P'):
        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
        rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = rgb_img
    
    # Resize
    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    
    # Save optimized version
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=quality, optimize=True)
    return ContentFile(buffer.getvalue(), name=image.name)
```

### Use in Model Save

Update `products/models.py`:

```python
from core.image_utils import resize_image

class ProductImage(models.Model):
    # ... existing fields ...
    
    def save(self, *args, **kwargs):
        if self.image:
            self.image = resize_image(self.image)
        super().save(*args, **kwargs)
```

## Version Management

### Preserve Image Versions

```python
# Store original and thumbnail versions
def store_product_image(sender, instance, **kwargs):
    if instance.image:
        # Store original
        original = instance.image
        instance.image.original = original
        
        # Generate thumbnail
        thumb = resize_image(instance.image, max_width=300)
        instance.image.thumbnail = thumb
```

## Monitoring and Maintenance

### S3 Cost Optimization

1. **Enable S3 Intelligent-Tiering**: Automatically moves data to cost-effective storage classes
2. **Set Lifecycle Policies**: Archive old objects
3. **Monitor Usage**: Use S3 Storage Lens

### S3 Lifecycle Rules

```json
{
    "Rules": [
        {
            "Id": "DeleteOldVersions",
            "Status": "Enabled",
            "NoncurrentVersionExpirationInDays": 30
        },
        {
            "Id": "ArchiveOldFiles",
            "Status": "Enabled",
            "Transitions": [
                {
                    "Days": 90,
                    "StorageClass": "GLACIER"
                }
            ]
        }
    ]
}
```

### Monitor Bucket

```bash
# Get bucket size
aws s3 ls s3://ecommerce-prod-bucket --recursive --summarize

# Get bucket metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/S3 \
  --metric-name BucketSizeBytes \
  --dimensions Name=BucketName,Value=ecommerce-prod-bucket \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-31T23:59:59Z \
  --period 86400 \
  --statistics Average
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 403 Forbidden | Check IAM user permissions and bucket policy |
| Images not loading | Verify S3 bucket name and region in settings |
| Slow uploads | Check uploading from far regions; use S3 Transfer Acceleration |
| High costs | Review S3 Intelligent-Tiering, enable compression |
| CloudFront not serving | Wait for distribution to fully deploy (~15 min) |

## Security Best Practices

1. **Enable versioning**: Protect against accidental deletions
   ```bash
   aws s3api put-bucket-versioning \
     --bucket ecommerce-prod-bucket \
     --versioning-configuration Status=Enabled
   ```

2. **Enable server-side encryption**:
   ```bash
   aws s3api put-bucket-encryption \
     --bucket ecommerce-prod-bucket \
     --server-side-encryption-configuration '{...}'
   ```

3. **Block public access** (if not needed):
   ```bash
   aws s3api put-public-access-block \
     --bucket ecommerce-prod-bucket \
     --public-access-block-configuration \
     "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
   ```

4. **Use HTTPS**: All connections to S3 should be encrypted

5. **Rotate IAM credentials**: Regularly create new access keys

## References

- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [django-storages S3 Backend](https://django-storages.readthedocs.io/en/latest/backends/amazon-s3.html)
- [boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
