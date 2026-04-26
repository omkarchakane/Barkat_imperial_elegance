"""
Simple static files copy command that doesn't rely on Django's finders
Includes both custom static files and Django app static files (including admin)
"""
import os
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from django.apps import apps


class Command(BaseCommand):
    help = 'Copy static files manually (workaround for collectstatic issues)'

    def handle(self, *args, **options):
        base_dir = Path(settings.BASE_DIR)
        static_root = Path(settings.STATIC_ROOT)

        # Create STATIC_ROOT if it doesn't exist
        static_root.mkdir(parents=True, exist_ok=True)
        self.stdout.write(f'Static root: {static_root}')

        total_copied = 0

        # Copy from STATICFILES_DIRS (custom static files)
        self.stdout.write(self.style.WARNING('\n=== Copying custom static files ==='))
        static_dirs = settings.STATICFILES_DIRS
        for static_dir in static_dirs:
            static_path = Path(static_dir) if isinstance(static_dir, str) else static_dir
            
            if not static_path.is_absolute():
                static_path = base_dir / static_path
            
            self.stdout.write(f'From: {static_path}')
            
            if not static_path.exists():
                self.stdout.write(self.style.WARNING(f'  ⚠️ Does not exist'))
                continue
            
            # Copy all files recursively
            for root, dirs, files in os.walk(static_path):
                for file in files:
                    src_file = Path(root) / file
                    rel_path = src_file.relative_to(static_path)
                    dst_file = static_root / rel_path
                    
                    # Create destination directory
                    dst_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(src_file, dst_file)
                    self.stdout.write(f'  ✓ {rel_path}')
                    total_copied += 1

        # Copy from installed Django apps (including admin, contrib, etc.)
        self.stdout.write(self.style.WARNING('\n=== Copying Django app static files ==='))
        for app_config in apps.get_app_configs():
            app_static_dir = Path(app_config.module.__file__).parent / 'static'
            
            if app_static_dir.exists():
                self.stdout.write(f'From app {app_config.name}: {app_static_dir}')
                
                # Copy all files recursively
                for root, dirs, files in os.walk(app_static_dir):
                    for file in files:
                        src_file = Path(root) / file
                        rel_path = src_file.relative_to(app_static_dir)
                        dst_file = static_root / rel_path
                        
                        # Create destination directory
                        dst_file.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Copy file
                        shutil.copy2(src_file, dst_file)
                        self.stdout.write(f'  ✓ {rel_path}')
                        total_copied += 1

        self.stdout.write(self.style.SUCCESS(f'\n✓ Copied {total_copied} static files'))

