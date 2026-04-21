from django.shortcuts import render,redirect
from django.db import models
from .models import Product,Review,Cart,UserRegister,OfferPoster,ProductImage,Wishlist

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
    product =Product.objects.get(id=id)  #! show the single data 
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
    product = Product.objects.get(id=id)
    reviews = Review.objects.filter(product=product)
    avg_rating = sum([r.rating for r in reviews]) / len(reviews) if reviews else 0
    
    return render(request, "quick_view.html", {
        'product': product,
        'avg_rating': avg_rating
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
    if request.method =="POST":
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']

        if UserRegister.objects.filter(email=email).exists():
             return redirect('/register')

        UserRegister.objects.create(
            name = name,
            email= email,
            password = password
        )

        return redirect ('/login')
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
    del request.session['user']
    return redirect('/login')    


def is_logged_in(request):
    return request.session.get('user') is not None