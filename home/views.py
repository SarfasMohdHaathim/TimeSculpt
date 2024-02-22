# Django imports
from django.shortcuts import (
    get_object_or_404, redirect, render
)
from django.views.generic import TemplateView
from django.db.models import Q, Max
from django.contrib.auth import (
    logout, authenticate, login
)
from django.views import View
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import razorpay
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import  timedelta

from .models import *
from api.models import User
from .serializers import WatchSerializer, WatchImageSerializer ,OrderPlacedSerializer,UserSerializer
from rest_framework.views import APIView


@api_view(['POST'])
def create_watch(request, format=None):
    if request.method == 'POST':
        serializer = WatchSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_watches(request, format=None):
    if request.method == 'GET':
        watches = Watch.objects.all()
        serialized_data = []
        for watch in watches:
            actual_price = watch.actual_price() 
            serialized_watch = WatchSerializer(watch).data
            serialized_watch['actual_price'] = actual_price  
            serialized_data.append(serialized_watch)
        return Response(serialized_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def list_orders(request, format=None):
    if request.method == 'GET':
        orders = OrderPlaced.objects.all()
        serialized_orders = OrderPlacedSerializer(orders, many=True)
        return Response(serialized_orders.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def list_users(request, format=None):
    if request.method == 'GET':
        users = User.objects.filter(is_staff=False)
        serialized_user = UserSerializer(users, many=True)
        return Response(serialized_user.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def list_staffs(request, format=None):
    if request.method == 'GET':
        users = User.objects.filter(is_staff=True)
        serialized_user = UserSerializer(users, many=True)
        return Response(serialized_user.data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
def delete_watch(request, pk, format=None):
    watch = get_object_or_404(Watch, pk=pk)
    if request.method == 'DELETE':
        watch.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def watch_detail(request, pk, format=None):
    watch = get_object_or_404(Watch, pk=pk)
    if request.method == 'GET':
        serialized_data = []
        serialized_watch = WatchSerializer(watch).data
        actual_price = watch.actual_price() 
        serialized_watch['actual_price'] = actual_price  
        serialized_data.append(serialized_watch)
        return Response(serialized_watch, status=status.HTTP_200_OK)
    
@api_view(['PUT', 'PATCH'])
def edit_watch(request, pk, format=None):
    watch = get_object_or_404(Watch, pk=pk)
    if request.method == 'PUT' or request.method == 'PATCH':
        print('===============================')
        serializer = WatchSerializer(watch, data=request.data, partial=True)  
        print('===============================',serializer.is_valid())
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class WatchImageCreateAPIView(APIView):
    def post(self, request, format=None):
        serializer = WatchImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WatchImageDeleteAPIView(APIView):
    def delete(self, request, pk, format=None):
        try:
            watch_image = WatchImage.objects.get(pk=pk)
        except WatchImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        watch_image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
@api_view(['GET'])
def watch_image_list(request, pk, format=None):
    if request.method == 'GET':
        watch = Watch.objects.get(id=pk)
        watch_images = WatchImage.objects.filter(watch_name=watch)
        serializer = WatchImageSerializer(watch_images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    

class HomeView(TemplateView):
    template_name = 'a.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        print(current_user)
        context['product'] = Watch.objects.all()[0:5]
        context['f_product'] = Watch.objects.filter(discount__gt=5).order_by('-discount')[:5]
        context['p_product'] = Watch.objects.filter(discount__gt=5).order_by('-price')[:5]
        print()
        return context


class WatchDetailView(TemplateView):
    template_name = 'watch.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        watch_id = kwargs['watch_id']
        watch = Watch.objects.get(id=watch_id)
        watch_image=WatchImage.objects.filter(watch_name=watch)
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
        context['watch_image'] = watch_image
        print(watch_image,'============================')
        context['related_products'] = related_products
        print(related_products)
        return context
    


class WatchView(TemplateView):
    template_name = 'shop.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        gender = self.request.GET.getlist('gender')
        brands = self.request.GET.getlist('brand')
        styles = self.request.GET.getlist('style')
        strap_materials = self.request.GET.getlist('strap_material')
        dial_types = self.request.GET.getlist('dial_type')
        dial_colours = self.request.GET.getlist('dial_colour')
        dial_shapes = self.request.GET.getlist('dial_shape')
        sort_option = self.request.GET.get('sort')

        watches = Watch.objects.all()
        if gender:
            watches = watches.filter(gender__in=gender)
        if brands:
            watches = watches.filter(brands__in=brands)
        if styles:
            watches = watches.filter(style__in=styles)
        if strap_materials:
            watches = watches.filter(strap_material__in=strap_materials)
        if dial_types:
            watches = watches.filter(dial_type__in=dial_types)
        if dial_colours:
            watches = watches.filter(dial_colour__in=dial_colours)
        if dial_shapes:
            watches = watches.filter(dial_shape__in=dial_shapes)


        if sort_option == '1': 
            watches = watches.order_by('watch_name')
        elif sort_option == '2': 
            watches = watches.order_by('watch_name')
        elif sort_option == '3':  
            watches = watches.order_by('watch_name')
        elif sort_option == '4':
            watches = watches.order_by('-watch_name')
        elif sort_option == '5': 
            watches = watches.order_by('price')
        elif sort_option == '6': 
            watches = watches.order_by('-price')
        elif sort_option == '7':  
            watches = watches.order_by('created_at')
        elif sort_option == '8': 
            watches = watches.order_by('-created_at')    

        paginator = Paginator(watches, 10)  
        page = self.request.GET.get('page')

        try:
            watches = paginator.page(page)
        except PageNotAnInteger:
            watches = paginator.page(1)
        except EmptyPage:
            watches = paginator.page(paginator.num_pages)

        context['products'] = watches
        context['paginator'] = paginator  

        context['GENDER_CHOICES'] = Watch.GENDER_CHOICES
        context['BRAND_CHOICES'] = Watch.BRAND_CHOICES
        context['STYLE_CHOICES'] = Watch.STYLE_CHOICES
        context['STRAP_MATERIAL_CHOICES'] = Watch.STRAP_MATERIAL_CHOICES
        context['DIAL_TYPE_CHOICES'] = Watch.DIAL_TYPE_CHOICES
        context['DIAL_COLOUR_CHOICES'] = Watch.DIAL_COLOUR_CHOICES
        context['DIAL_SHAPE_CHOICES'] = Watch.DIAL_SHAPE_CHOICES
        context['selected_brands'] = brands
        context['selected_gender'] = gender
        context['selected_styles'] = styles
        context['selected_strap_materials'] = strap_materials
        context['selected_dial_types'] = dial_types
        context['selected_dial_colours'] = dial_colours
        context['selected_dial_shapes'] = dial_shapes

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
    def post(self, request, *args, **kwargs):
        user = request.user
        cart = Cart.objects.filter(user=user)
        famount = 0
        for c in cart:
            print(c.watch_name.actual_price(),'============')
            famount +=c.watch_name.price
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
            
            context['first_name'] = request.user.first_name
            context['last_name'] = request.user.last_name
            current_user = request.user
            context['cart'] = Cart.objects.filter(user=current_user)
            cart = Cart.objects.filter(user=current_user)
            famount = 0
            pamount = 0
            damount = 0
            for c in cart:
                pamount += c.watch_name.price
                famount +=c.watch_name.actual_price()
                damount += c.watch_name.discounted_price()
            
            context['famount'] = famount
            context['pamount'] = pamount
            context['damount'] = damount
            address_exists =Address.objects.filter(user=request.user).exists()
            if address_exists :
                context['address'] = Address.objects.get(user=request.user)
            
            return render(request,'checkout.html',context)
        else:
            pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        context['cart'] = Cart.objects.filter(user=current_user)
        cart = Cart.objects.filter(user=current_user)
        famount = 0
        pamount = 0
        damount = 0
        for c in cart:
            pamount += c.watch_name.price
            famount +=c.watch_name.actual_price()
            damount += c.watch_name.discounted_price()
        
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
                    famount +=c.watch_name.actual_price()
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
                    famount +=1
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


def register(request):
    if request.method == 'POST':
        f_name = request.POST.get('f_name')
        l_name = request.POST.get('l_name')
        email = request.POST.get('register_email')
        password = request.POST.get('register_password')
        confirm_password = request.POST.get('register_confirm_password')
        username = email.split('@')[0]

        if password == confirm_password:
            try:
                user = User.objects.create_user(username=username,first_name=f_name,last_name=l_name,
                                                email=email, password=password)
                user.save()
                print('authentication take place========================================')
                user = authenticate(request, username=username, password=password)
                print('no authentication========================================')
                login(request, user)
                messages.success(request, 'You have successfully registered and logged in.')
                return redirect('home')
            except:
                messages.error(request, 'Email Already Registered, Please Log In')
                return redirect(request.path + '#tab-item-register')
        else:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')
    else:
        return render(request, 'register.html')
    

def userlogin(request):
    if request.method == 'POST':
        email = request.POST['login_email']
        password = request.POST['login_password']
        username = email.split('@')[0]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid Credential')
            return redirect('userlogin')
    else:
        return render(request, 'login.html')
    


def dashboard(request):
    user = request.user  
    fname = user.first_name
    lname = user.last_name
    context = {'fname': fname, 'lname': lname}
    return render(request, 'account_dashboard.html', context)




def account_address(request):
    context={}
    context['first_name'] = request.user.first_name
    context['last_name'] = request.user.last_name
    address_exists =Address.objects.filter(user=request.user).exists()
    if address_exists :
        context['address'] = Address.objects.get(user=request.user)
       
    return render(request, 'account_address.html', context)


def wishlist(request):
    user=request.user
    wishlist=Wishlist.objects.filter(user=user)
    context={'wishlist':wishlist}
    return render(request,'wishlist.html',context)


def brands(request):
    return render(request,'brand.html')


def stores(request):
    return render(request,'store.html')

def addtowishlist(request,pk):
    user=request.user
    product=Watch.objects.get(id=pk)
    Wishlist.objects.create(user=user,watch_name=product).save()
    return redirect('wishlist')


def removewishlist(request,pk):
    wishlist=Wishlist.objects.get(id=pk)
    wishlist.delete()
    return redirect('wishlist')


def offers(request):
    gender = request.GET.getlist('gender')
    brands = request.GET.getlist('brand')
    styles = request.GET.getlist('style')
    strap_materials = request.GET.getlist('strap_material')
    dial_types = request.GET.getlist('dial_type')
    dial_colours = request.GET.getlist('dial_colour')
    dial_shapes = request.GET.getlist('dial_shape')

    watches = Watch.objects.all()
    if gender:
        watches = watches.filter(gender__in=gender)
    if brands:
        watches = watches.filter(brands__in=brands)
    if styles:
        watches = watches.filter(style__in=styles)
    if strap_materials:
        watches = watches.filter(strap_material__in=strap_materials)
    if dial_types:
        watches = watches.filter(dial_type__in=dial_types)
    if dial_colours:
        watches = watches.filter(dial_colour__in=dial_colours)
    if dial_shapes:
        watches = watches.filter(dial_shape__in=dial_shapes)

    paginator = Paginator(watches, 10)  
    page = request.GET.get('page')

    try:
        watches = paginator.page(page)
    except PageNotAnInteger:
        watches = paginator.page(1)
    except EmptyPage:
        watches = paginator.page(paginator.num_pages)
    context={}
    context['products'] = watches
    context['paginator'] = paginator  

    context['GENDER_CHOICES'] = Watch.GENDER_CHOICES
    context['BRAND_CHOICES'] = Watch.BRAND_CHOICES
    context['STYLE_CHOICES'] = Watch.STYLE_CHOICES
    context['STRAP_MATERIAL_CHOICES'] = Watch.STRAP_MATERIAL_CHOICES
    context['DIAL_TYPE_CHOICES'] = Watch.DIAL_TYPE_CHOICES
    context['DIAL_COLOUR_CHOICES'] = Watch.DIAL_COLOUR_CHOICES
    context['DIAL_SHAPE_CHOICES'] = Watch.DIAL_SHAPE_CHOICES
    context['selected_brands'] = brands
    context['selected_gender'] = gender
    context['selected_styles'] = styles
    context['selected_strap_materials'] = strap_materials
    context['selected_dial_types'] = dial_types
    context['selected_dial_colours'] = dial_colours
    context['selected_dial_shapes'] = dial_shapes

    return render(request,'offer.html',context)