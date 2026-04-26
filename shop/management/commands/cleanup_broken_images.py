"""
Django management command to clean up broken media file paths and mark for re-upload
This is useful when local files don't exist but database records do.

Usage: python manage.py cleanup_broken_images
"""

from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from shop.models import Product, ProductImage, OfferPoster


class Command(BaseCommand):
    help = 'List and analyze broken image references in database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Analyzing image references...'))
        self.stdout.write(self.style.WARNING('\n' + '='*60))

        broken_products = []
        broken_images = []
        broken_posters = []

        # Check Product images
        self.stdout.write(self.style.WARNING('\nProduct Images:'))
        products = Product.objects.filter(image__isnull=False).exclude(image='')
        
        for product in products:
            if product.image and hasattr(product.image, 'name'):
                file_path = product.image.name
                exists = default_storage.exists(file_path)
                status = '✓ Found' if exists else '✗ BROKEN'
                self.stdout.write(f'  {status}: {product.name} -> {file_path}')
                if not exists:
                    broken_products.append(product)

        # Check ProductImage images
        self.stdout.write(self.style.WARNING('\nProductImage Gallery Items:'))
        prod_images = ProductImage.objects.filter(image__isnull=False).exclude(image='')
        
        for img in prod_images:
            if img.image and hasattr(img.image, 'name'):
                file_path = img.image.name
                exists = default_storage.exists(file_path)
                status = '✓ Found' if exists else '✗ BROKEN'
                self.stdout.write(f'  {status}: {img.product.name} -> {file_path}')
                if not exists:
                    broken_images.append(img)

        # Check OfferPoster images
        self.stdout.write(self.style.WARNING('\nOffer Posters:'))
        posters = OfferPoster.objects.filter(image__isnull=False).exclude(image='')
        
        for poster in posters:
            if poster.image and hasattr(poster.image, 'name'):
                file_path = poster.image.name
                exists = default_storage.exists(file_path)
                status = '✓ Found' if exists else '✗ BROKEN'
                self.stdout.write(f'  {status}: {poster.title} -> {file_path}')
                if not exists:
                    broken_posters.append(poster)

        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.WARNING(f'\nBROKEN FILES SUMMARY:'))
        self.stdout.write(f'  Products: {len(broken_products)}')
        self.stdout.write(f'  Gallery Images: {len(broken_images)}')
        self.stdout.write(f'  Posters: {len(broken_posters)}')
        self.stdout.write(f'  TOTAL: {len(broken_products) + len(broken_images) + len(broken_posters)}')
        self.stdout.write(self.style.SUCCESS('='*60))

        if broken_products or broken_images or broken_posters:
            self.stdout.write(self.style.ERROR('\n⚠️  ACTION REQUIRED:'))
            self.stdout.write('1. Re-upload images via Django Admin')
            self.stdout.write('2. Then run: python manage.py migrate_images_to_cloudinary')
            self.stdout.write('3. This will move them to Cloudinary storage')
