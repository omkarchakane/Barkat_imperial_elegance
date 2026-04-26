"""
Simple static files copy command that doesn't rely on Django's finders
"""
import os
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Copy static files manually (workaround for collectstatic issues)'

    def handle(self, *args, **options):
        base_dir = Path(settings.BASE_DIR)
        static_root = Path(settings.STATIC_ROOT)
        static_dirs = settings.STATICFILES_DIRS

        # Create STATIC_ROOT if it doesn't exist
        static_root.mkdir(parents=True, exist_ok=True)
        self.stdout.write(f'Static root: {static_root}')

        total_copied = 0

        for static_dir in static_dirs:
            static_path = Path(static_dir) if isinstance(static_dir, str) else static_dir
            
            if not static_path.is_absolute():
                static_path = base_dir / static_path
            
            self.stdout.write(f'Copying from: {static_path}')
            
            if not static_path.exists():
                self.stdout.write(self.style.WARNING(f'  ⚠️ Does not exist: {static_path}'))
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

        self.stdout.write(self.style.SUCCESS(f'\n✓ Copied {total_copied} static files'))
