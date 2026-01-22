from .models import Cart

def cart_count(request):
    count = 0
    if request.session.get('user'):
        count =Cart.objects.filter(username=request.session['user']).count()
    return {'cart_count': count}    

#! settings.py line 65