from .models import Cart

def base_common(request):
    cart_item={}
    cart_count=0
    famount=0
    if request.user.is_authenticated:
        
        try:
            user = request.user
            cart_item = Cart.objects.filter(user=user)
            cart_count=cart_item.count()
            famount=0
            for c in cart_item:
                famount += c.watch_name.actual_price()
        except Cart.DoesNotExist:
            pass

    return {
        'cart_item': cart_item,'famount':famount,'cart_count':cart_count
    }