from django.shortcuts import render,redirect
from .models import Product,Review,Cart,UserRegister
def home(request):
    search = request.GET.get('search')
    if search :
        products = Product.objects.filter(name__icontains=search) #!Case-insensitive search
    else:
        products = Product.objects.all()    
    return render(request,"home.html",{'products':products})

def product(request, id):
    product =Product.objects.get(id=id)  #! show the single data 
    reviews = Review.objects.filter(product=product)
    if request.method == "POST":
        if not request.session.get('user'):
            return redirect('/login')
       
        Review.objects.create(username=request.session['user'],product=product,comment=request.POST['comment'])
    return render(request,"product.html",{
        'product':product,
        'reviews':reviews
    })

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