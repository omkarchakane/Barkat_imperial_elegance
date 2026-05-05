import random
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.db import models
from django.shortcuts import get_object_or_404, render,redirect
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from .models import Product,Review,Cart,UserRegister,OfferPoster,ProductImage,Wishlist,Order,OrderItem

REGISTRATION_PENDING_KEY = 'pending_registration'
REGISTRATION_OTP_KEY = 'registration_otp'
REGISTRATION_OTP_EXPIRY_KEY = 'registration_otp_expiry'
REGISTRATION_OTP_MINUTES = 10

def home(request):
    search = request.GET.get('search')
    if search :
        products = Product.objects.filter(name__icontains=search) #!Case-insensitive search
    else:
        products = Product.objects.all()
    
    # Get new arrival products for carousel
    new_arrivals = Product.objects.filter(is_new_arrival=True)[:8]
    # Get active posters
    posters = OfferPoster.objects.filter(active=True)
    
    # Get user's wishlist for heart icon display
    wishlist_products = []
    if request.session.get('user'):
        wishlist_products = list(Wishlist.objects.filter(username=request.session['user']).values_list('product_id', flat=True))
    
    return render(request,"home.html",{
        'products':products, 
        'new_arrivals':new_arrivals, 
        'posters':posters,
        'wishlist_products': wishlist_products
    })

def product(request, id):
    product = get_object_or_404(Product.objects.prefetch_related('images'), id=id)  #! show the single data 
    reviews = Review.objects.filter(product=product).order_by('-created_at')
    
    # Calculate average rating
    avg_rating = 0
    if reviews:
        avg_rating = sum([r.rating for r in reviews]) / len(reviews)
    
    # Get related products (same fabric or color)
    related_products = Product.objects.filter(
        models.Q(fabric=product.fabric) | models.Q(color=product.color)
    ).exclude(id=product.id)[:4]
    
    # Check if in wishlist
    in_wishlist = False
    if request.session.get('user'):
        in_wishlist = Wishlist.objects.filter(username=request.session['user'], product=product).exists()
    
    if request.method == "POST":
        if not request.session.get('user'):
            return redirect('/login')
        
        rating = request.POST.get('rating', 5)
        Review.objects.create(username=request.session['user'],product=product,comment=request.POST['comment'], rating=rating)
        return redirect(f'/product/{id}')
    
    return render(request,"product.html",{
        'product':product,
        'reviews':reviews,
        'avg_rating': avg_rating,
        'related_products': related_products,
        'in_wishlist': in_wishlist
    })

# Quick view for product modal
def quick_view(request, id):
    product = get_object_or_404(Product.objects.prefetch_related('images'), id=id)
    reviews = Review.objects.filter(product=product)
    avg_rating = sum([r.rating for r in reviews]) / len(reviews) if reviews else 0
    
    return render(request, "quick_view.html", {
        'product': product,
        'avg_rating': avg_rating,
        'reviews': reviews,
    })

# Wishlist views
def add_wishlist(request, id):
    if not request.session.get('user'):
        return redirect('/login')
    
    product = Product.objects.get(id=id)
    Wishlist.objects.get_or_create(username=request.session['user'], product=product)
    return redirect(request.META.get('HTTP_REFERER', '/'))

def remove_wishlist(request, id):
    if not request.session.get('user'):
        return redirect('/login')
    
    Wishlist.objects.filter(username=request.session['user'], product_id=id).delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))

def wishlist(request):
    if not request.session.get('user'):
        return redirect('/login')
    
    items = Wishlist.objects.filter(username=request.session['user']).select_related('product')
    return render(request, "wishlist.html", {'items': items})

def add_cart(request,id):
    if not request.session.get('user'):
        return redirect ('/login')
    product = Product.objects.get(id=id)
    cart_item = Cart.objects.filter(username=request.session['user'], product=product).first()
    if cart_item:
        cart_item.quantity += 1
        cart_item.save()
    else:
        Cart.objects.create(
            username = request.session['user'],
            product=product,
            quantity=1
        )
    return redirect('/cart')

def buy_now(request,id):
    if not request.session.get('user'):
        return redirect('/login')
    product = Product.objects.get(id=id)
    cart_item = Cart.objects.filter(username=request.session['user'], product=product).first()
    if cart_item:
        cart_item.quantity += 1
        cart_item.save()
    else:
        Cart.objects.create(
            username = request.session['user'],
            product=product,
            quantity=1
        )
    return redirect('/checkout/order-summary/')

def cart(request):
    if not request.session.get('user'):
        return redirect ('/login')
    
    items=Cart.objects.filter(username=request.session['user'])
    total=0

    for i in items:
        total += i.product.price * i.quantity   #! calculate total price

    return render (request,"cart.html",{
        'items':items,
        'total':total
    })     #! Send data to templates

def remove_cart(request,id):
    Cart.objects.filter(id=id, username=request.session['user']).delete()
    return redirect ('/cart')

def increase_qty(request,id):
    item = Cart.objects.get(id=id, username=request.session['user'])
    item.quantity+=1
    item.save()
    return redirect('/cart')

def decrease_qty(request,id):
    item = Cart.objects.get(id=id, username=request.session['user'])
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    return redirect('/cart')   


def clear_registration_session(request):
    request.session.pop(REGISTRATION_PENDING_KEY, None)
    request.session.pop(REGISTRATION_OTP_KEY, None)
    request.session.pop(REGISTRATION_OTP_EXPIRY_KEY, None)


def send_registration_otp(request, name, email):
    otp = f"{random.randint(100000, 999999)}"
    expires_at = timezone.now() + timedelta(minutes=REGISTRATION_OTP_MINUTES)

    request.session[REGISTRATION_OTP_KEY] = otp
    request.session[REGISTRATION_OTP_EXPIRY_KEY] = expires_at.isoformat()
    request.session.modified = True

    subject = "Barkat verification code"
    message = (
        f"Hi {name},\n\n"
        f"Your Barkat verification code is: {otp}\n"
        f"This code expires in {REGISTRATION_OTP_MINUTES} minutes.\n\n"
        "If you did not request this, you can ignore this email."
    )

    send_mail(
        subject,
        message,
        getattr(settings, 'DEFAULT_FROM_EMAIL', None),
        [email],
        fail_silently=False,
    )

def register(request):
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not name or not email or not password:
            messages.error(request, 'Please fill all required fields.')
            return redirect('/register')

        if UserRegister.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists.')
            return redirect('/register')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('/register')

        request.session[REGISTRATION_PENDING_KEY] = {
            'name': name,
            'email': email,
            'password': password,
        }

        try:
            send_registration_otp(request, name, email)
        except Exception:
            clear_registration_session(request)
            messages.error(
                request,
                'We could not send verification email. Please check email settings and try again.',
            )
            return redirect('/register')

        messages.success(request, 'Verification code sent to your email.')
        return redirect('/verify-email/')
    return render (request,"register.html")


def verify_email(request):
    pending = request.session.get(REGISTRATION_PENDING_KEY)
    if not pending:
        messages.info(request, 'Start registration first.')
        return redirect('/register')

    if request.method == "POST":
        if request.POST.get('action') == 'resend':
            try:
                send_registration_otp(request, pending['name'], pending['email'])
            except Exception:
                messages.error(
                    request,
                    'We could not resend verification email. Please try again.',
                )
            else:
                messages.success(request, 'A new verification code has been sent.')
            return redirect('/verify-email/')

        otp_input = request.POST.get('otp', '').strip()
        stored_otp = request.session.get(REGISTRATION_OTP_KEY)
        expiry_raw = request.session.get(REGISTRATION_OTP_EXPIRY_KEY)
        expiry_time = parse_datetime(expiry_raw) if expiry_raw else None

        if not otp_input:
            messages.error(request, 'Please enter the verification code.')
            return redirect('/verify-email/')

        if not stored_otp or not expiry_time or timezone.now() > expiry_time:
            messages.error(request, 'Verification code expired. Please resend a new code.')
            return redirect('/verify-email/')

        if otp_input != stored_otp:
            messages.error(request, 'Invalid verification code.')
            return redirect('/verify-email/')

        if UserRegister.objects.filter(email=pending['email']).exists():
            clear_registration_session(request)
            messages.error(request, 'This email is already registered. Please log in.')
            return redirect('/login')

        UserRegister.objects.create(
            name=pending['name'],
            email=pending['email'],
            password=pending['password'],
        )

        clear_registration_session(request)
        messages.success(request, 'Email verified. Account created successfully.')
        return redirect('/login')

    return render(request, "verify_email.html", {'pending_email': pending.get('email', '')})

def login(request):
    return render(request,"login.html")

def login_check(request):
    if request.method =="POST":
        email = request.POST['email']
        password = request.POST['password']

        user = UserRegister.objects.filter(email=email,password=password)

        if user:
            request.session['user'] = email   #!Session start
            request.session['customer_name'] = user[0].name
            return redirect('/')
        else:
            return redirect('/login')
    else:
        return redirect ('/login')    
    
def logout(request):
    del request.session['user']
    return redirect('/login')    


def is_logged_in(request):
    return request.session.get('user') is not None


def product_reviews(request, id):
    product = Product.objects.get(id=id)
    reviews = Review.objects.filter(product=product).order_by('-created_at')

    avg_rating = 0
    if reviews:
        avg_rating = sum([r.rating for r in reviews]) / len(reviews)

    return render(request, "product_reviews.html", {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating
    })


def checkout_order_summary(request):
    if not request.session.get('user'):
        return redirect('/login')

    items = Cart.objects.filter(username=request.session['user'])
    total = 0

    for i in items:
        total += i.product.price * i.quantity

    if not items:
        return redirect('/cart')

    return render(request, "checkout_order_summary.html", {
        'items': items,
        'total': total
    })


def checkout_shipping(request):
    if not request.session.get('user'):
        return redirect('/login')

    items = Cart.objects.filter(username=request.session['user'])
    total = 0

    for i in items:
        total += i.product.price * i.quantity

    if not items:
        return redirect('/cart')

    if request.method == "POST":
        request.session['checkout_data'] = {
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'email': request.POST.get('email'),
            'phone': request.POST.get('phone'),
            'address': request.POST.get('address'),
            'city': request.POST.get('city'),
            'state': request.POST.get('state'),
            'postal_code': request.POST.get('postal_code'),
            'country': request.POST.get('country', 'India'),
        }
        return redirect('/checkout/payment/')

    user = UserRegister.objects.filter(email=request.session.get('user')).first()
    order = {
        'first_name': user.name.split()[0] if user else '',
        'last_name': user.name.split()[1] if user and len(user.name.split()) > 1 else '',
        'email': request.session.get('user'),
        'phone': '',
        'address': '',
        'city': '',
        'state': '',
        'postal_code': '',
        'country': 'India',
    }

    return render(request, "checkout_shipping.html", {
        'items': items,
        'total': total,
        'order': order
    })


def checkout_payment(request):
    if not request.session.get('user'):
        return redirect('/login')

    items = Cart.objects.filter(username=request.session['user'])
    total = 0

    for i in items:
        total += i.product.price * i.quantity

    if not items:
        return redirect('/cart')

    if request.method == "POST":
        payment_method = request.POST.get('payment_method', 'cod')
        checkout_data = request.session.get('checkout_data', {})

        order = Order.objects.create(
            username=request.session['user'],
            total_amount=total,
            payment_method=payment_method,
            first_name=checkout_data.get('first_name', ''),
            last_name=checkout_data.get('last_name', ''),
            email=checkout_data.get('email', ''),
            phone=checkout_data.get('phone', ''),
            address=checkout_data.get('address', ''),
            city=checkout_data.get('city', ''),
            state=checkout_data.get('state', ''),
            postal_code=checkout_data.get('postal_code', ''),
            country=checkout_data.get('country', 'India'),
            status='confirmed'
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        items.delete()

        if 'checkout_data' in request.session:
            del request.session['checkout_data']

        return redirect(f'/checkout/success/{order.id}/')

    return render(request, "checkout_payment.html", {
        'items': items,
        'total': total
    })


def checkout_success(request, order_id):
    if not request.session.get('user'):
        return redirect('/login')

    order = Order.objects.get(id=order_id)

    if order.username != request.session['user']:
        return redirect('/')

    for item in order.items.all():
        item.total = item.price * item.quantity

    return render(request, "checkout_success.html", {
        'order': order
    })
