import os
import sys
import django
import urllib.request
import time

# initialize Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barkat.settings')
django.setup()

from shop.models import Product, OfferPoster


def list_products():
    """Print all products with new-arrival flag."""
    products = Product.objects.all()
    print(f"Total products: {products.count()}")
    for p in products:
        print(f"{p.id}: {p.name}  new={p.is_new_arrival} offer={p.offer_text}")

def list_posters():
    """Print all offer posters."""
    posters = OfferPoster.objects.all()
    print(f"Total posters: {posters.count()}")
    for pt in posters:
        print(f"{pt.id}: {pt.title} active={pt.active} image={pt.image}")


def mark_all_new():
    """Mark every product in the database as a new arrival."""
    for p in Product.objects.all():
        p.is_new_arrival = True
        p.save()
    print("All products marked as new arrivals.")

def add_poster(title="Festive Offer", image_path="posters/sample.jpg"):
    """Create a sample poster. `image_path` relative to MEDIA_ROOT."""
    if not OfferPoster.objects.filter(title=title).exists():
        pt = OfferPoster.objects.create(title=title, image=image_path, active=True)
        print(f"Created poster: {pt}")
        return pt
    else:
        print(f"Poster '{title}' already exists.")
        return None

def remove_poster(title=None, id=None):
    """Remove a poster by title or id."""
    qs = OfferPoster.objects.all()
    if title:
        qs = qs.filter(title=title)
    if id:
        qs = qs.filter(id=id)
    count = qs.count()
    if count:
        qs.delete()
        print(f"Deleted {count} poster(s)")
    else:
        print("No matching poster found to delete.")

def toggle_poster(id, active=None):
    """Toggle active state or set explicitly for a poster."""
    try:
        pt = OfferPoster.objects.get(id=id)
        if active is None:
            pt.active = not pt.active
        else:
            pt.active = active
        pt.save()
        print(f"Poster {pt.id} active={pt.active}")
    except OfferPoster.DoesNotExist:
        print("Poster not found.")


def add_sample(name="Example New Saree"):
    """Create a sample new-arrival product if it doesn't already exist."""
    if not Product.objects.filter(name=name).exists():
        sample = Product.objects.create(
            name=name,
            price=1500,
            image='products/Saree.webp',
            description='Automatically added for testing',
            is_new_arrival=True,
        )
        print(f"Created sample product: {sample}")
        return sample
    else:
        print(f"Sample product '{name}' already exists.")
        return None


def set_offer(product_name="Example New Saree", offer_text="20% OFF"):
    """Set the `offer_text` field on a product by name.

    Defaults target the sample new saree used elsewhere in tests.
    """
    p = Product.objects.filter(name=product_name).first()
    if p:
        p.offer_text = offer_text
        p.save()
        print(f"Offer text updated for {p.name}")
    else:
        print("Product not found")


def check_image(url='http://127.0.0.1:8000/media/products/Saree.webp'):
    """Attempt to fetch an image URL and print status/headers."""
    try:
        response = urllib.request.urlopen(url)
        print(f"Image Status: {response.status}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Content-Length: {response.headers.get('Content-Length')}")
    except Exception as e:
        print(f"Error: {e}")


def check_carousel():
    """Fetch the home page and report carousel statistics."""
    try:
        response = urllib.request.urlopen('http://127.0.0.1:8000/')
        html = response.read().decode('utf-8')
    except Exception as e:
        print(f"Error accessing site: {e}")
        return

    items = html.count('carousel-item')
    badges = html.count('new-badge')
    images = html.count('<img')
    print("CAROUSEL STATISTICS:")
    print(f"  • items    : {items}")
    print(f"  • badges   : {badges}")
    print(f"  • images   : {images}")

    # show product names
    names = []
    pos = 0
    while True:
        idx = html.find('carousel-card-title', pos)
        if idx == -1:
            break
        start = html.find('>', idx) + 1
        end = html.find('<', start)
        names.append(html[start:end].strip())
        pos = end
    if names:
        print("PRODUCTS IN CAROUSEL:")
        for n in names:
            print(f"  - {n}")


if __name__ == '__main__':
    # simple command line interface
    if len(sys.argv) < 2:
        print("Usage: python carousel_utils.py [list|mark|add|check|offer|checkimg|posters|rmposter|toggle]")
        sys.exit(1)
    cmd = sys.argv[1].lower()
    if cmd == 'list':
        list_products()
    elif cmd == 'mark':
        mark_all_new()
    elif cmd == 'add':
        add_sample()
    elif cmd == 'check':
        check_carousel()
    elif cmd == 'offer':
        pname = sys.argv[2] if len(sys.argv) >= 3 else "Example New Saree"
        off = sys.argv[3] if len(sys.argv) >= 4 else "20% OFF"
        set_offer(pname, off)
    elif cmd == 'checkimg':
        url = sys.argv[2] if len(sys.argv) >= 3 else 'http://127.0.0.1:8000/media/products/Saree.webp'
        check_image(url)
    elif cmd == 'posters':
        if len(sys.argv) == 2:
            list_posters()
        else:
            sub = sys.argv[2].lower()
            if sub == 'add' and len(sys.argv) >= 4:
                title = sys.argv[3]
                img = sys.argv[4] if len(sys.argv) >=5 else 'posters/sample.jpg'
                add_poster(title=title, image_path=img)
            elif sub == 'remove' and len(sys.argv) >= 3:
                title = sys.argv[3] if len(sys.argv) >=4 else None
                pid = int(sys.argv[4]) if len(sys.argv) >=5 else None
                remove_poster(title=title, id=pid)
            elif sub == 'toggle' and len(sys.argv) >= 4:
                pid = int(sys.argv[3])
                state = None
                if len(sys.argv) >=5:
                    state = sys.argv[4].lower() in ('1','true','yes')
                toggle_poster(pid, active=state)
            else:
                print("Usage: python carousel_utils.py posters [add|remove|toggle] ...")
    elif cmd == 'rmposter':
        title = sys.argv[2] if len(sys.argv) >=3 else None
        pid = int(sys.argv[3]) if len(sys.argv) >=4 else None
        remove_poster(title=title, id=pid)
    elif cmd == 'toggle':
        pid = int(sys.argv[2])
        state = None
        if len(sys.argv) >=4:
            state = sys.argv[3].lower() in ('1','true','yes')
        toggle_poster(pid, active=state)
    else:
        print(f"Unknown command '{cmd}'")
        print("Valid commands: list, mark, add, check, posters, rmposter, toggle")
