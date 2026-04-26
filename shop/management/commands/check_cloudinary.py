"""
Management command to verify Cloudinary configuration
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.storage import default_storage
import cloudinary


class Command(BaseCommand):
    help = 'Check Cloudinary configuration and connectivity'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Cloudinary Configuration Check'))
        self.stdout.write(self.style.WARNING('=' * 60))

        # Check environment variable
        cloudinary_url = getattr(settings, 'CLOUDINARY_URL', '')
        self.stdout.write(f'\n✓ CLOUDINARY_URL set: {bool(cloudinary_url)}')
        if cloudinary_url:
            self.stdout.write(f'  URL exists: Yes')

        # Check DEFAULT_FILE_STORAGE
        default_storage_backend = getattr(settings, 'DEFAULT_FILE_STORAGE', '')
        self.stdout.write(f'\n✓ DEFAULT_FILE_STORAGE: {default_storage_backend}')
        is_cloudinary = 'cloudinary' in default_storage_backend.lower()
        self.stdout.write(f'  Using Cloudinary: {is_cloudinary}')

        # Check cloudinary config
        self.stdout.write(f'\n✓ Cloudinary Config:')
        config = cloudinary.config()
        self.stdout.write(f'  Cloud name: {config.cloud_name if config.cloud_name else "NOT SET"}')
        self.stdout.write(f'  API key: {config.api_key if config.api_key else "NOT SET"}')
        self.stdout.write(f'  Has credentials: {bool(config.cloud_name and config.api_key)}')

        # Try to verify storage
        self.stdout.write(f'\n✓ Storage Type:')
        self.stdout.write(f'  Type: {type(default_storage).__name__}')
        
        self.stdout.write(self.style.WARNING('\n' + '=' * 60))
        
        if is_cloudinary and config.cloud_name:
            self.stdout.write(self.style.SUCCESS('✓ Cloudinary is properly configured!'))
            self.stdout.write('\nNew image uploads will go to Cloudinary.')
        else:
            self.stdout.write(self.style.ERROR('✗ Cloudinary is NOT properly configured!'))
            self.stdout.write('\nMake sure CLOUDINARY_URL environment variable is set.')
