"""
Django management command to migrate existing local images to Cloudinary
and update database records to point to Cloudinary URLs.

Usage: python manage.py migrate_images_to_cloudinary
"""

import os
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from shop.models import Product, ProductImage, OfferPoster


class Command(BaseCommand):
    help = 'Migrate local images to Cloudinary storage and update database records'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting image migration to Cloudinary...'))

        migrated_count = 0
        skipped_count = 0

        # Migrate Product images
        self.stdout.write(self.style.WARNING('\nMigrating Product images...'))
        products = Product.objects.filter(image__isnull=False).exclude(image='')

        for product in products:
            try:
                if product.image and hasattr(product.image, 'name'):
                    old_path = product.image.name
                    # Check if file exists in local storage
                    if default_storage.exists(old_path):
                        # Read the file
                        file_content = default_storage.open(old_path, 'rb').read()
                        
                        # Create new file in Cloudinary storage
                        new_filename = os.path.basename(old_path)
                        product.image.save(new_filename, file_content, save=False)
                        product.save()
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Migrated product image: {product.name} - {new_filename}'
                            )
                        )
                        migrated_count += 1
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'⊘ File not found locally: {old_path} (Product: {product.name})'
                            )
                        )
                        skipped_count += 1
                else:
                    skipped_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error migrating {product.name}: {str(e)}')
                )
                skipped_count += 1

        # Migrate ProductImage images
        self.stdout.write(self.style.WARNING('\nMigrating ProductImage entries...'))
        product_images = ProductImage.objects.filter(image__isnull=False).exclude(image='')

        for prod_img in product_images:
            try:
                if prod_img.image and hasattr(prod_img.image, 'name'):
                    old_path = prod_img.image.name
                    # Check if file exists in local storage
                    if default_storage.exists(old_path):
                        # Read the file
                        file_content = default_storage.open(old_path, 'rb').read()
                        
                        # Create new file in Cloudinary storage
                        new_filename = os.path.basename(old_path)
                        prod_img.image.save(new_filename, file_content, save=False)
                        prod_img.save()
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Migrated product image: {prod_img.product.name} - {new_filename}'
                            )
                        )
                        migrated_count += 1
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'⊘ File not found locally: {old_path} (Product: {prod_img.product.name})'
                            )
                        )
                        skipped_count += 1
                else:
                    skipped_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error migrating image for {prod_img.product.name}: {str(e)}')
                )
                skipped_count += 1

        # Migrate OfferPoster images
        self.stdout.write(self.style.WARNING('\nMigrating OfferPoster images...'))
        posters = OfferPoster.objects.filter(image__isnull=False).exclude(image='')

        for poster in posters:
            try:
                if poster.image and hasattr(poster.image, 'name'):
                    old_path = poster.image.name
                    # Check if file exists in local storage
                    if default_storage.exists(old_path):
                        # Read the file
                        file_content = default_storage.open(old_path, 'rb').read()
                        
                        # Create new file in Cloudinary storage
                        new_filename = os.path.basename(old_path)
                        poster.image.save(new_filename, file_content, save=False)
                        poster.save()
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Migrated poster image: {poster.title} - {new_filename}'
                            )
                        )
                        migrated_count += 1
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'⊘ File not found locally: {old_path} (Poster: {poster.title})'
                            )
                        )
                        skipped_count += 1
                else:
                    skipped_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error migrating poster {poster.title}: {str(e)}')
                )
                skipped_count += 1

        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS(f'Migration Complete!'))
        self.stdout.write(self.style.SUCCESS(f'✓ Successfully migrated: {migrated_count} images'))
        self.stdout.write(self.style.WARNING(f'⊘ Skipped/Not found: {skipped_count}'))
        self.stdout.write(self.style.SUCCESS('='*60))
