#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput 2>/dev/null || python manage.py copy_static
python manage.py migrate_images_to_cloudinary 2>/dev/null || echo "Image migration skipped or already done"
