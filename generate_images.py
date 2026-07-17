#!/usr/bin/env python
"""Generate placeholder images for products."""
import os
import django
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.core.files.base import ContentFile
from products.models import Product
from django.conf import settings

# Create media directories if they don't exist
media_root = settings.MEDIA_ROOT
product_images_dir = os.path.join(media_root, 'product_images')
os.makedirs(product_images_dir, exist_ok=True)

# Define colors for different categories
category_colors = {
    'Electronics': '#3498db',  # Blue
    'Fashion': '#e74c3c',      # Red
    'Home & Garden': '#2ecc71', # Green
}

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def generate_placeholder_image(product_name, category_name):
    """Generate a placeholder image for a product."""
    # Create a new image
    width, height = 400, 400
    
    # Get background color based on category
    color = category_colors.get(category_name, '#95a5a6')
    bg_color = hex_to_rgb(color)
    
    # Create image with semi-transparent background
    image = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(image)
    
    # Add semi-transparent overlay
    overlay = Image.new('RGBA', (width, height), (255, 255, 255, 50))
    image = image.convert('RGBA')
    image = Image.alpha_composite(image, overlay)
    image = image.convert('RGB')
    draw = ImageDraw.Draw(image)
    
    # Draw text on image
    text = product_name
    font_size = 30
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Word wrap text
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        test_line = ' '.join(current_line)
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] > width - 40:  # Leave 20px margin on each side
            lines.append(' '.join(current_line[:-1]))
            current_line = [word]
    lines.append(' '.join(current_line))
    
    # Calculate text position
    total_text_height = len(lines) * 40
    y_start = (height - total_text_height) // 2
    
    # Draw text centered
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        y = y_start + (i * 40)
        # Draw with white text and subtle shadow
        draw.text((x+2, y+2), line, font=font, fill=(0, 0, 0, 50))  # Shadow
        draw.text((x, y), line, font=font, fill='white')
    
    return image

# Generate images for products
count = 0
for product in Product.objects.all():
    if not product.image:
        try:
            # Generate placeholder image
            image = generate_placeholder_image(product.name, product.category.name)
            
            # Save to BytesIO
            image_io = BytesIO()
            image.save(image_io, format='PNG', quality=85)
            image_io.seek(0)
            
            # Create filename
            filename = f"placeholder_{product.slug}.png"
            
            # Save to product
            product.image.save(
                os.path.join('product_images', filename),
                ContentFile(image_io.getvalue()),
                save=True
            )
            
            print(f"✓ Created image for: {product.name}")
            count += 1
        except Exception as e:
            print(f"✗ Error creating image for {product.name}: {e}")

print(f"\n✓ Created {count} product images!")
