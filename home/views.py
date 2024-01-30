from django.shortcuts import get_object_or_404,redirect,render
from django.views.generic import TemplateView
from .models import *
from django.db.models import Q
from django.contrib.auth import logout
from django.views import View
from django.contrib import messages
from django.conf import settings
import razorpay
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta

class HomeView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        print(current_user)
        context['product'] = Watch.objects.all()
        return context


class WatchDetailView(TemplateView):
    template_name = 'details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        watch_id = kwargs['watch_id']
        watch = Watch.objects.get(id=watch_id)
        related_products = Watch.objects.filter(
            Q(brands=watch.brands) |
            Q(gender=watch.gender) |
            Q(dial_type=watch.dial_type) |
            Q(dial_colour=watch.dial_colour) |
            Q(dial_shape=watch.dial_shape) |
            Q(style=watch.style) |
            Q(strap_material=watch.strap_material)
        ).exclude(id=watch.id)[:4]
        context['watch'] = watch
        context['related_products'] = related_products
        print(related_products)
        return context
    


class WatchView(TemplateView):
    template_name = 'shop.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        gender = self.request.GET.get('gender')
        brands = self.request.GET.getlist('brand')

        watches = Watch.objects.all()
        if gender:
            watches = watches.filter(gender=gender)
        if brands:
            watches = watches.filter(brands__in=brands)
        context['product'] = watches
        print(gender,'------------------------------------------------')
        context['GENDER_CHOICES'] = Watch.GENDER_CHOICES 
        context['BRAND_CHOICES'] = Watch.BRAND_CHOICES 
        return context



def userlogout(request):
    logout(request)
    return redirect('home')


class AddToCartView(LoginRequiredMixin, View):
    def get(self, request, pk):
        user = request.user
        product = get_object_or_404(Watch, id=pk)
        Cart.objects.create(user=user, watch_name=product)
        messages.success(request, f'{product.watch_name} {product.gender} Carted Successfully')
        return redirect(request.META.get('HTTP_REFERER', 'home'))
        

class CartView(LoginRequiredMixin,TemplateView):
    template_name = 'cart.html'
    login_url = '/userlogin/'
    def get_famount(self, cart):
        famount = 0
        pamount = 0
        damount = 0
        for c in cart:
            pamount += c.watch_name.price
            famount += c.watch_name.actual_price()
            damount += c.watch_name.discounted_price()
        return famount, pamount, damount

    def post(self, request, *args, **kwargs):
        user = request.user
        cart = Cart.objects.filter(user=user)
        famount = 0
        for c in cart:
            famount += c.watch_name.actual_price()
        razoramount = int(famount * 100)
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        data = {'amount': razoramount, "currency": "INR", "receipt": "order_rcptid_12"}
        payment_response = client.order.create(data=data)
        order_id = payment_response['id']
        order_status = payment_response['status']
        if order_status == 'created':
            payment = Payment.objects.create(
                user=user,
                amount=famount,
                razorpay_order_id=order_id,
                razorpay_payment_status=order_status
            )
            payment.save()
            email = request.user.email
            context = {'famount': famount, 'razoramount': razoramount, 'email': email, 'payment': payment}
            
            context['first_name'] = self.request.user.first_name
            context['last_name'] = self.request.user.last_name
            current_user = self.request.user
            context['cart'] = Cart.objects.filter(user=current_user)
            cart = Cart.objects.filter(user=current_user)
            famount, pamount, damount = self.get_famount(cart)
            context['famount'] = famount
            context['pamount'] = pamount
            context['damount'] = damount
            address_exists =Address.objects.filter(user=self.request.user).exists()
            if address_exists :
                context['address'] = Address.objects.get(user=self.request.user)
            
            return render(request,'checkout.html',context)
        else:
            pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        context['cart'] = Cart.objects.filter(user=current_user)
        cart = Cart.objects.filter(user=current_user)
        famount, pamount, damount = self.get_famount(cart)
        context['famount'] = famount
        context['pamount'] = pamount
        context['damount'] = damount
        context['current_user'] = current_user
        print(famount)
        address_exists =Address.objects.filter(user=self.request.user).exists()
        if address_exists :
            context['address'] = Address.objects.get(user=self.request.user)
        return context



class RegisterView(TemplateView):
    template_name = 'register.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = Watch.objects.all()
        return context





class CheckOut(LoginRequiredMixin,TemplateView):
    template_name = 'checkout.html'
    login_url = '/userlogin/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['first_name'] = self.request.user.first_name
            context['last_name'] = self.request.user.last_name
            address_exists =Address.objects.filter(user=self.request.user).exists()
            if address_exists :
                context['address'] = Address.objects.get(user=self.request.user)
                current_user = self.request.user
                context['cart'] = Cart.objects.filter(user=current_user)
                cart = Cart.objects.filter(user=current_user)
                pamount,famount,damount=0,0,0
                for c in cart:
                    pamount += c.watch_name.price
                    famount += c.watch_name.actual_price()
                    damount += c.watch_name.discounted_price()
                print(context)
                context['famount'] = famount
                context['pamount'] = pamount
                context['damount'] = damount
        return context
    def post(self, request, *args, **kwargs):
        country = request.POST.get('country')
        street_address = request.POST.get('street_address')
        city = request.POST.get('city')
        zipcode = request.POST.get('zipcode')
        phone = request.POST.get('phone')
        try:
            Address.objects.create(
                user=request.user,
                country=country,
                street_address=street_address,
                city=city,
                zipcode=zipcode,
                phone=phone,
            )
            messages.success(request, 'Your address has been saved successfully!')
        except:
            address = Address.objects.get( user=request.user)
            address.country = country
            address.street_address = street_address
            address.city = city
            address.zipcode = zipcode
            address.phone = phone
            address.save()
            messages.success(request, 'Your address has been updated successfully!')
        return redirect('checkout') 
    

class ShippingAddress(LoginRequiredMixin,TemplateView):
    template_name = 'shipping_address.html'
    login_url = '/userlogin/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['first_name'] = self.request.user.first_name
            context['last_name'] = self.request.user.last_name
            address_exists =Address.objects.filter(user=self.request.user).exists()
            if address_exists :
                context['address'] = Address.objects.get(user=self.request.user)
                current_user = self.request.user
                context['cart'] = Cart.objects.filter(user=current_user)
                cart = Cart.objects.filter(user=current_user)
                pamount,famount,damount=0,0,0
                for c in cart:
                    pamount += c.watch_name.price
                    famount += c.watch_name.actual_price()
                    damount += c.watch_name.discounted_price()
                print(context)
                context['famount'] = famount
                context['pamount'] = pamount
                context['damount'] = damount
        return context
    def post(self, request, *args, **kwargs):
        country = request.POST.get('country')
        street_address = request.POST.get('street_address')
        city = request.POST.get('city')
        zipcode = request.POST.get('zipcode')
        phone = request.POST.get('phone')
        try:
            Address.objects.create(
                user=request.user,
                country=country,
                street_address=street_address,
                city=city,
                zipcode=zipcode,
                phone=phone,
            )
            messages.success(request, 'Your address has been saved successfully!')
        except:
            address = Address.objects.get( user=request.user)
            address.country = country
            address.street_address = street_address
            address.city = city
            address.zipcode = zipcode
            address.phone = phone
            address.save()
            messages.success(request, 'Your address has been updated successfully!')
        return redirect('cart_view') 
    


@require_POST
def delete_cart_item(request, pk):
    item = get_object_or_404(Cart, pk=pk)
    item.delete()
    return redirect('cart_view')


def payment_done(request):
    response=request.POST
    params_dict={
            'razorpay_order_id':response.get('razorpay_order_id'),
            'razorpay_payment_id':response.get('razorpay_payment_id'),
            'razorpay_signature':response.get('razorpay_signature')
      }
    client=razorpay.Client(auth=(settings.RAZOR_KEY_ID,settings.RAZOR_KEY_SECRET))
    print(params_dict)
    status=client.utility.verify_payment_signature(params_dict)
    print(status)
    print(params_dict.get("razorpay_order_id"))
    payment=Payment.objects.get(razorpay_order_id__icontains=params_dict.get("razorpay_order_id"))
    user=payment.user.username
    payment.razorpay_payment_id=params_dict.get("razorpay_payment_id")
    payment.paid=True
    payment.save()
    username=User.objects.get(username=user)
    cart_product=Cart.objects.filter(user=username)
    orderplaced_list = []
    cart=[]
    context={}
    famount=0
    for cart_p in cart_product:
        orderplaced = OrderPlaced.objects.create(user=username, product=cart_p.watch_name, payment=payment)
        orderplaced_list.append(orderplaced)
        cart.append(cart_p.watch_name)
        famount += cart_p.watch_name.actual_price()
    cart_product.delete()
    context['orderplaced_list']= orderplaced_list
    context['cart_product']= cart
    context['famount']= famount
    print(context,'===================================')
    return redirect('orders')


def orders(request):
    order=OrderPlaced.objects.filter(user=request.user)
    total=0
    i=0
    order_id=order[0].payment.razorpay_order_id
    order_date=order[0].ordered_date
    delivary_date = order_date + timedelta(days=5)
    o_product=[]
    for order in order:
        o_product.append(order.product)
        total+=order.product.actual_price()
        i+=1
    context={'order_id':order_id,'total':total,'i':i,'order_date':order_date,'delivary_date':delivary_date,'o_product':o_product}
    return render(request,'order_complete.html',context)


def orders_page(request):
    orders = OrderPlaced.objects.filter(user=request.user)
    total = 0
    for order in orders:
        total += order.product.actual_price()
    context = {'orders': orders, 'total': total}
    return render(request, 'account_order.html', context)