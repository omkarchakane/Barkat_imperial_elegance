from django.contrib import messages
from django.db import models
from django.shortcuts import get_object_or_404, render,redirect
from .models import Product,Review,Cart,UserRegister,OfferPoster,ProductImage,Wishlist,Order,OrderItem

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

        UserRegister.objects.create(
            name=name,
            email=email,
            password=password,
        )
        messages.success(request, 'Your account has been created. Please log in.')
        return redirect('/login')
    return render (request,"register.html")

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
    request.session.pop('user', None)
    request.session.pop('customer_name', None)
    return redirect('/login')    


def profile(request):
    if not request.session.get('user'):
        return redirect('/login')

    user_email = request.session['user']
    user = UserRegister.objects.filter(email=user_email).first()

    orders = list(
        Order.objects.filter(username=user_email)
        .prefetch_related('items__product')
        .order_by('-order_date')
    )
    wishlist_count = Wishlist.objects.filter(username=user_email).count()

    status_counts = {key: 0 for key, _ in Order.ORDER_STATUS_CHOICES}
    status_badge_map = {
        'pending': 'warning',
        'confirmed': 'primary',
        'shipped': 'info',
        'delivered': 'success',
        'cancelled': 'danger',
    }

    for order in orders:
        status_counts[order.status] = status_counts.get(order.status, 0) + 1
        order.total_items = sum(item.quantity for item in order.items.all())
        order.badge_class = status_badge_map.get(order.status, 'secondary')

    return render(request, "profile.html", {
        'user_email': user_email,
        'customer_name': user.name if user else request.session.get('customer_name', ''),
        'orders': orders,
        'status_counts': status_counts,
        'total_orders': len(orders),
        'wishlist_count': wishlist_count,
    })


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
