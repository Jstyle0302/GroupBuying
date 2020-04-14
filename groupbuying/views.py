import json
import operator
import math
import datetime

from collections import defaultdict
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.urls import reverse
from django.http import HttpResponse, Http404
from django.http import HttpResponseForbidden
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.utils.timezone import is_aware, make_aware
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.cache import cache

from groupbuying.forms import LoginForm, RegistrationForm, ProductForm, VendorInfoForm, CustomerInfoForm
from groupbuying.models import Product, CustomerInfo, VendorInfo, Rating, UserProfile, OrderUnit, OrderBundle, Category
from django.db.models import Q
from django.db.models import Avg
from functools import reduce
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags



def PAGESIZE_CONSTANT():
    return 2


def get_shopEditPage_context(request):
    context = {}
    cur_vendor_info = VendorInfo.objects.get(vendor_id=request.user.id)

    context['menu'] = get_menu(cur_vendor_info.vendor_id)
    context['productForm'] = ProductForm()
    context['vendorInfo'] = cur_vendor_info
    context['vendorForm'] = VendorInfoForm(
        initial={'description': cur_vendor_info.description}, instance=cur_vendor_info)

    return context


def home_page(request):
    context = {}
    return render(request, 'groupbuying/home.html', context)


def orderList_page(request):
    context = {}
    customerInfo = CustomerInfo.objects.filter(Q(id=str(request.user.id)))[0]
    orderUnits = OrderUnit.objects.filter(Q(buyer=customerInfo))
    context['orders'] = []
    orderbundleId = []
    for orderUnit in orderUnits.distinct():
        if orderUnit.orderbundle.id in orderbundleId:
            continue

        order = {
            'order_id': orderUnit.orderbundle.id,
            'name': orderUnit.orderbundle.vendor.name,
            'description': orderUnit.orderbundle.vendor.description,
            'image': "https://upload.wikimedia.org/wikipedia/en/thumb/8/85/Panda_Express_logo.svg/1200px-Panda_Express_logo.svg.png"
        }
        context['orders'].append(order)
        orderbundleId.append(orderUnit.orderbundle.id)

    return render(request, 'groupbuying/orderList.html', context)


def share_page(request, order_id):
    context = {}
    context['shop_name'] = "Starbucks"
    context['description'] = "Very expensive and unhealthy food."
    context['logo'] = "https://upload.wikimedia.org/wikipedia/en/thumb/d/d3/Starbucks_Corporation_Logo_2011.svg/1200px-Starbucks_Corporation_Logo_2011.svg.png"
    context['menu'] = {
        'all': {

        }
    }

    context['productForm'] = ProductForm()
    context['vendorForm'] = VendorInfoForm()
    context['description'] = "Hi Shine, please insert the vendor's description here"
    context['categories'] = Category.objects.all()
    context['products'] = Product.objects.all()
    context['vendorInfo'] = VendorInfo.objects.all()  # TODO: delte lated
    # context = {'categories': categories, 'products': products, 'errors': errors}
    orderbundle = OrderBundle.objects.filter(Q(id=str(order_id)))[0]
    context['founder'] = orderbundle.holder.name
    context['order_id'] = order_id

    return render(request, 'groupbuying/shop.html', context)

def send_email_page(request, order_id):
    context = {}
    orderbundle = OrderBundle.objects.filter(Q(id=str(order_id)))[0]
    customerInfo = CustomerInfo.objects.filter(Q(id=str(request.user.id)))[0]

    if orderbundle.holder.id == request.user.id:
        context['isFounder'] = True
        orderUnits = OrderUnit.objects.filter(Q(orderbundle=orderbundle))

    else:
        context['isFounder'] = True
        orderUnits = OrderUnit.objects.filter(
            Q(buyer=customerInfo) & Q(orderbundle=orderbundle))

    context['order_id'] = orderbundle.id
    context['shop'] = orderbundle.vendor.name
    context['founder'] = orderbundle.holder.name

    context['receipt'] = {}
    context['receipt']['orders'] = []
    context['receipt']['summary'] = {}
    total_price = 0

    for orderUnit in orderUnits:
        dictOrder = {}
        dictOrder['username'] = (orderUnit.buyer.name)
        print(orderUnit.buyer.name)
        total_price += int(orderUnit.product.price)*int(orderUnit.quantity)
        dictOrder['order'] = []
        subOrder = {
            'product': orderUnit.product.name,
            'count': orderUnit.quantity,
            'price': orderUnit.product.price
        }
        dictOrder['order'].append(subOrder)
        context['receipt']['orders'].append(dictOrder)

    context['receipt']['summary']['total'] = total_price


    subject = str(request.user.username) + "'s order at " + orderbundle.vendor.name + "(order_id:" + str(orderbundle.id) + ")" 
    html_message = render_to_string('groupbuying/order_email.html', context)
    plain_message = strip_tags(html_message)
    from_email = 'groupbuyingTeam23@gmail.com'
    to_email = [request.user.email]

    send_mail(subject, plain_message, from_email, to_email, html_message=html_message, fail_silently=False)

    ## send_mail(subject, plain_message, from_email, [request.user.email], fail_silently=False)

    return redirect('shop')

def show_order_page(request, order_id):
    context = {}
    orderbundle = OrderBundle.objects.filter(Q(id=str(order_id)))[0]
    customerInfo = CustomerInfo.objects.filter(Q(id=str(request.user.id)))[0]

    if orderbundle.holder.id == request.user.id:
        context['isFounder'] = True
        orderUnits = OrderUnit.objects.filter(Q(orderbundle=orderbundle))

    else:
        context['isFounder'] = False
        orderUnits = OrderUnit.objects.filter(
            Q(buyer=customerInfo) & Q(orderbundle=orderbundle))

    context['order_id'] = orderbundle.id
    context['shop'] = orderbundle.vendor.name
    context['founder'] = orderbundle.holder.name
    context['receipt'] = {}
    context['receipt']['orders'] = []
    context['receipt']['summary'] = {}
    context['receipt']['summary']['order'] = []
    context['checkout_to_shopper'] = 1

    for orderUnit in orderUnits:

        if orderUnit.isPaid == False:
            continue
        dictOrder = {}
        dictOrder['username'] = (orderUnit.buyer.name)
        dictOrder['order'] = []
        dictOrder['description'] = orderUnit.comment

        subOrder = {
            'product': orderUnit.product.name,
            'count': orderUnit.quantity,
            'price': orderUnit.product.price
        }
        summary = {
            'product': orderUnit.product.name,
            'count': orderUnit.quantity,
            'price': orderUnit.product.price
        }

        dictOrder['order'].append(subOrder)
        context['receipt']['orders'].append(dictOrder)

        is_product_exist = 0
        for order in context['receipt']['summary']['order']:
            if orderUnit.product.name in order['product']:
                is_product_exist = 1
                order['count'] =  str(int(order['count']) +  int(orderUnit.quantity))


        if is_product_exist == 0:
            context['receipt']['summary']['order'].append(summary)


    total_price = 0

    for order in context['receipt']['summary']['order']:
        order['price'] = (int(order['count']) * int(order['price']))
        total_price += order['price']

    context['receipt']['summary']['total'] = total_price

    return render(request, 'groupbuying/order.html', context)


@login_required
def order_page(request, order_id):
    context = {}
    if 'product_id' not in request.POST or not request.POST['product_id'] or \
            'product_number' not in request.POST or not request.POST['product_number']:
        return render(request, 'groupbuying/order.html', context)

    customerInfo = CustomerInfo.objects.filter(Q(id=str(request.user.id)))[0]
    product = Product.objects.filter(Q(id=str(request.POST['product_id'])))[0]
    vendorInfo = VendorInfo.objects.filter(Q(id=str(product.vendor.id)))[0]

    if order_id == "new":
        new_orderbundle = OrderBundle(holder=customerInfo,
                                      vendor=vendorInfo)
        new_orderbundle.save()
    else:
        new_orderbundle = OrderBundle.objects.filter(Q(id=str(order_id)))[0]

    new_orderUnit = OrderUnit(
        buyer=customerInfo,
        product=product,
        quantity=int(request.POST['product_number']),
        comment='omg',
        orderTime=datetime.datetime.now(),
        orderDate=datetime.datetime.now(),
        deliverTime=datetime.datetime.now(),
        deliverDate=datetime.datetime.now(),
        isPaid=False,
        orderbundle=new_orderbundle
    )
    new_orderUnit.save()

    context['checkout_to_holder'] = 1
    context['isFounder'] = True
    context['order_id'] = new_orderbundle.id
    context['order_unit_id'] = new_orderUnit.id
    context['shop'] = vendorInfo.name
    context['founder'] = new_orderbundle.holder.name
    context['receipt'] = {
        'orders': [{
            'username': new_orderUnit.buyer.name,
            'order': [{
                'product': product.name,
                'count': request.POST['product_number'],
                'price': product.price
            }],
            'total': int(request.POST['product_number']) * int(product.price)
        }],
        'summary': {
            'order': [{
                'product': product.name,
                'count': request.POST['product_number'],
                'price': product.price
            }],
            'total': int(request.POST['product_number']) * int(product.price)
        }
    }

    return render(request, 'groupbuying/order.html', context)

@login_required
def checkout_to_holder(request, order_unit_id):
    context = {}
    orderUnit = OrderUnit.objects.filter(Q(id=str(order_unit_id)))[0]
    if 'orderDescription' in request.POST and request.POST['orderDescription']:
        orderUnit.comment = request.POST['orderDescription']
   
    orderUnit.isPaid = True 
    orderUnit.save()
    #print("checkout_to_holder")
    #print(order_unit_id)
    #print(orderUnit.isPaid)
    return redirect('shop')


@login_required
def checkout_to_shopper(request, order_id):
    context = {}
    orderbundle = OrderBundle.objects.filter(Q(id=str(order_id)))[0]
    customerInfo = CustomerInfo.objects.filter(Q(id=str(request.user.id)))[0]

    if orderbundle.holder.id == request.user.id:
        context['isFounder'] = True
        orderUnits = OrderUnit.objects.filter(Q(orderbundle=orderbundle))

    else:
        context['isFounder'] = True
        orderUnits = OrderUnit.objects.filter(
            Q(buyer=customerInfo) & Q(orderbundle=orderbundle))

    context['order_id'] = orderbundle.id
    context['shop'] = orderbundle.vendor.name
    context['founder'] = orderbundle.holder.name

    context['receipt'] = {}
    context['receipt']['orders'] = []
    context['receipt']['summary'] = {}
    context['receipt']['summary']['order'] = []
    
    if 'orderDescription' in request.POST and request.POST['orderDescription']:
        context['receipt']['description'] = request.POST['orderDescription']


    for orderUnit in orderUnits:

        if orderUnit.isPaid == False:
            continue
        dictOrder = {}
        dictOrder['username'] = (orderUnit.buyer.name)
        dictOrder['order'] = []
        dictOrder['description'] = orderUnit.comment

        subOrder = {
            'product': orderUnit.product.name,
            'count': orderUnit.quantity,
            'price': orderUnit.product.price
        }
        summary = {
            'product': orderUnit.product.name,
            'count': orderUnit.quantity,
            'price': orderUnit.product.price
        }

        dictOrder['order'].append(subOrder)
        context['receipt']['orders'].append(dictOrder)

        is_product_exist = 0
        for order in context['receipt']['summary']['order']:
            if orderUnit.product.name in order['product']:
                is_product_exist = 1
                order['count'] =  str(int(order['count']) +  int(orderUnit.quantity))


        if is_product_exist == 0:
            context['receipt']['summary']['order'].append(summary)


    total_price = 0

    for order in context['receipt']['summary']['order']:
        order['price'] = (int(order['count']) * int(order['price']))
        total_price += order['price']

    context['receipt']['summary']['total'] = total_price

    subject = str(request.user.username) + "'s order at " + orderbundle.vendor.name + "(order_id:" + str(orderbundle.id) + ")" 
    html_message = render_to_string('groupbuying/order_email.html', context)
    plain_message = strip_tags(html_message)
    from_email = 'groupbuyingTeam23@gmail.com'
    to_email = [request.user.email]

    send_mail(subject, plain_message, from_email, to_email, html_message=html_message, fail_silently=False)

    ## send_mail(subject, plain_message, from_email, [request.user.email], fail_silently=False)

    return redirect('shop')




@login_required
def profile_page(request, user_id):
    context = {}
    customerInfo = CustomerInfo.objects.filter(Q(id=str(user_id)))[0]
    context['username'] = customerInfo.name
    context['description'] = customerInfo.description
    context['orders'] = ['Pizza Hut', 'Cold Stone', 'Jeff']
    context['followers'] = ['Shine', 'Charles', 'Ari', 'En-ting', 'Ting']
    context['subcribes'] = ['Starbucks', 'Pandas', 'Subway']
    context['photo'] = "https://cdn.business2community.com/wp-content/uploads/2017/08/blank-profile-picture-973460_640.png"
    context['customerInfo'] = customerInfo

    return render(request, 'groupbuying/profile.html', context)


def other_page(request):
    context = {}
    context['username'] = 'Jeff'
    context['description'] = 'Amazing!'
    context['orders'] = ['Pizza Hut', 'Cold Stone', 'Jeff']
    context['followers'] = ['Shine', 'Charles', 'Ari', 'En-ting', 'Ting']
    context['subcribes'] = ['Starbucks', 'Pandas', 'Subway']
    context['photo'] = "https://cdn.business2community.com/wp-content/uploads/2017/08/blank-profile-picture-973460_640.png"
    return render(request, 'groupbuying/others.html', context)


def get_menu(vendor_id):
    menu = {}
    categories = Category.objects.filter(vendor__id=vendor_id)
    categories_names = [obj.name for obj in categories]

    for name in categories_names:
        temp_pdict = {}
        sub_products = Product.objects.filter(
            vendor__id=vendor_id, category__name=name)
        for sub_product in sub_products:
            temp_pInfodict = {}
            temp_pInfodict['id'] = sub_product.id
            temp_pInfodict['price'] = sub_product.price
            temp_pInfodict['image'] = sub_product.image
            temp_pInfodict['description'] = sub_product.description
            temp_pdict[sub_product.name] = dict(temp_pInfodict)
            # print(temp_pdict)
        menu[name] = dict(temp_pdict)

    return menu


@login_required
def shopEdit_page(request):
    # print(request.GET)
    # print(request.user.id, type(request.user.id))
    # print(request.user.social_auth.values_list('provider'))
    # print(request.user.social_auth.get(user=request.user, provider="google-oauth2"))
    # instance = UserSocialAuth.objects.get(user=request.user, provider='facebook')

    context = {}
    # context = get_shopEditPage_context(request)

    return render(request, 'groupbuying/shopEdit.html', context)

# @login_required


def shop_page(request):
    context = {}
    context['shop_name'] = "Starbucks"
    context['description'] = "Very expensive and unhealthy food."
    context['logo'] = "https://upload.wikimedia.org/wikipedia/en/thumb/d/d3/Starbucks_Corporation_Logo_2011.svg/1200px-Starbucks_Corporation_Logo_2011.svg.png"
    context['menu'] = {
        'all': {

        }
    }
    context['posts'] = [{
        'id':1,
        'created_by': {
            'username': 'Shine'
        },
        'creation_time': 'today',
        'post': 'Delicious',
        'rating':5
    },{
        'id':2,
        'created_by': {
            'username': 'Yangming'
        },
        'creation_time': 'tomorrow',
        'post': 'Tasty',
        'rating':4
    }]

    context['productForm'] = ProductForm()
    context['vendorForm'] = VendorInfoForm()
    context['description'] = "Hi Shine, please insert the vendor's description here"
    context['limitCost'] = 5
    context['categories'] = Category.objects.all()
    context['products'] = Product.objects.all()
    # # TODO: get_the correct one
    context['vendorInfo'] = VendorInfo.objects.all()
    # context = {'categories': categories, 'products': products, 'errors': errors}

    return render(request, 'groupbuying/shop.html', context)


@login_required
def add_category(request):
    context = {}
    errors = []  # A list to record messages for any errors we encounter.

    # Adds the new item to the database if the request parameter is present
    if 'new_category' not in request.POST or not request.POST['new_category']:
        errors.append('You must enter text to add new category.')
    else:
        new_category = Category(name=request.POST['new_category'],
                                vendor=request.user)
        new_category.save()

    context = get_shopEditPage_context(request)

    return render(request, 'groupbuying/shopEdit.html', context)


@login_required
def get_product_photo(request, product_id):
    product = get_object_or_404(Product, pk=str(product_id))
    if not product.image:
        print("Cannot find photo")
        raise Http404

    return HttpResponse(product.image, content_type=product.content_type)


@login_required
def add_product(request):
    context = {}
    errors = []  # A list to record messages for any errors we encounter.

    if 'name' not in request.POST or not request.POST['name'] or \
            'price' not in request.POST or not request.POST['price']:
        errors.append(
            'You must have at least "name and price" for the product')
    else:
        new_product = Product(name=str(request.POST['name']),
                              description=str(request.POST['description']),
                              price=float(request.POST['price']),
                              sellerId=str(request.user.id),
                              isAvailable=True,
                              saleVolume=0,
                              vendor=request.user)

        category = Category.objects.filter(
            name=str(request.POST['current_category']), vendor=request.user)
        if len(category) > 0:
            new_product.category = category[0]
        else:
            print('FAIL: Cannot find correct category')
            new_product.category = None

        form = ProductForm(request.POST, request.FILES, instance=new_product)
        # form = ImageUploadForm(request.POST, request.FILES)

        # if not form.is_valid():
        #     form = ProductForm()
        # else:
        if form.is_valid():
            if 'image' in request.FILES:
                new_product.image = form.cleaned_data['image']
                new_product.content_type = form.cleaned_data['image'].content_type
            context['message'] = 'Product #{0} saved.'.format(new_product.id)
            form.save()
            # new_product.save()

    context = get_shopEditPage_context(request)

    return render(request, 'groupbuying/shopEdit.html', context)


@login_required
def update_product(request):
    context = {}
    errors = []  # A list to record messages for any errors we encounter.

    if 'name' not in request.POST or not request.POST['name'] or \
            'price' not in request.POST or not request.POST['price']:
        errors.append(
            'You must have at least "name and price" for the product')
    else:
        cur_product = Product.objects.get(pk=str(request.POST['product_id']))

        # cur_product = Product.objects.filter(pk=str(product_id))[0] # Note: remember index for filter
        form = ProductForm(request.POST, request.FILES, instance=cur_product)
        if form.is_valid():
            cur_product.name = str(request.POST['name'])
            cur_product.price = float(request.POST['price'])
            cur_product.description = str(request.POST['description'])
            if 'image' in request.FILES:
                cur_product.image = form.cleaned_data['image']
                cur_product.content_type = form.cleaned_data['image'].content_type
            form.save()
        else:
            print("FAIL: ProductForm is NOT valid")

    context['productForm'] = ProductForm()
    # context['vendorInfo'] = cur_vendor_info
    context['vendorForm'] = VendorInfoForm()
    context['categories'] = Category.objects.all()
    context['products'] = Product.objects.all()

    return render(request, 'groupbuying/shopEdit.html', context)


@login_required
def update_vendor_name(request):
    context = {}
    errors = []  # A list to record messages for any errors we encounter.
    cur_vendor_info = VendorInfo.objects.get(vendor_id=request.user.id)

    if 'vendor_name' not in request.POST or not request.POST['vendor_name']:
        errors.append('You must have enter the vendor name')
    else:
        cur_vendor_info.name = request.POST['vendor_name']
        cur_vendor_info.save()

    context = get_shopEditPage_context(request)

    return render(request, 'groupbuying/shopEdit.html', context)


@login_required
def update_vendor_info(request):
    context = {}
    errors = []  # A list to record messages for any errors we encounter.
    cur_vendor_info = VendorInfo.objects.get(vendor_id=request.user.id)

    if 'description' not in request.POST or not request.POST['description'] or \
            'image' not in request.FILES or not request.FILES['image']:
        errors.append(
            'You must have at least "description and image" for the vendor info')
    else:
        # cur_vendor_info = VendorInfo.objects.filter(userProfile__user__id=request.user.id)[0] # Note: need to check
        form = VendorInfoForm(request.POST, request.FILES,
                              instance=cur_vendor_info)

        if not form.is_valid():
            print("FALI: form is NOT valid")
        else:
            cur_vendor_info.description = request.POST['description']
            if 'image' in request.FILES:
                cur_vendor_info.image = form.cleaned_data['image']
                cur_vendor_info.content_type = form.cleaned_data['image'].content_type
            form.save()

    context = get_shopEditPage_context(request)

    return render(request, 'groupbuying/shopEdit.html', context)


@login_required
def rating_star(request):
    rating = ''
    if 'rating' in request.POST and request.POST['rating']:
        rating = request.POST['rating']

    customer_info = CustomerInfo.objects.filter(id=str(request.user.id)).first()
    target_info = VendorInfo.objects.filter(id=str(request.user.id)).first()

    new_rating = Rating(rating=float(rating),
                              rater=customer_info,
                              ratedTarget=target_info
                              )
    new_rating.save()
    
    return redirect('shop')

@login_required
def update_customer_info(request, user_id):
    context = {}
    errors = []  # A list to record messages for any errors we encounter.
    #cur_customer_info = CustomerInfo.objects.filter(Q(id=str(user_id)))[0]
    cur_customer_info = CustomerInfo.objects.filter(id=str(user_id)).first()

    if 'description' in request.POST and request.POST['description']:
        cur_customer_info.description = request.POST['description']
        form = CustomerInfoForm(
            request.POST, request.FILES, instance=cur_customer_info)
        if form.is_valid():
            form.save()

    if 'image' in request.FILES and request.FILES['image']:
        form = CustomerInfoForm(
            request.POST, request.FILES, instance=cur_customer_info)
        if not form.is_valid():
            print("form is NOT valid")
        else:
            print("form is valid")
            if 'image' in request.FILES:
                cur_customer_info.image = form.cleaned_data['image']
                cur_customer_info.content_type = form.cleaned_data['image'].content_type
            form.save()

    context['username'] = cur_customer_info.name
    context['description'] = cur_customer_info.description
    context['orders'] = ['Pizza Hut', 'Cold Stone', 'Jeff']
    context['followers'] = ['Shine', 'Charles', 'Ari', 'En-ting', 'Ting']
    context['subcribes'] = ['Starbucks', 'Pandas', 'Subway']
    context['customerInfo'] = cur_customer_info
    return render(request, 'groupbuying/profile.html', context)


def category_proc(obj):
    tag_tmp = (obj.tagList.split(','))
    tag_tmp = list(filter(None, tag_tmp))
    return tag_tmp


def rating_proc(obj):
    avg_rating = Rating.objects.values('ratedTarget').annotate(
        avg_rating=Avg('rating')).order_by('ratedTarget')

    if not avg_rating.filter(ratedTarget=int(obj.id)):
        # default rating
        return 3
    else:
        return float(
            avg_rating.filter(ratedTarget=int(obj.id))[0]['avg_rating'])


def search_text_proc(search_text):
    search_result = VendorInfo.objects.filter(Q(name__contains=search_text) | Q(
        address__contains=search_text) | Q(tagList__contains=search_text))

    return search_result


def fill_restaurant_info(obj):
    restaurant = {}
    restaurant['id'] = int(obj.id)
    restaurant['name'] = str(obj.name)
    restaurant['description'] = str(obj.description)
    # tag/category
    restaurant['categories'] = category_proc(obj)
    # rating
    restaurant['rating'] = rating_proc(obj)

    # TBD
    restaurant['price'] = 5
    if obj.image:
        restaurant['image'] = obj.image_url
    else:    
        restaurant['image'] = "https://upload.wikimedia.org/wikipedia/en/thumb/d/d3/Starbucks_Corporation_Logo_2011.svg/1200px-Starbucks_Corporation_Logo_2011.svg.png"

    return restaurant


def get_all_tags():
    all_tag = []

    for obj in VendorInfo.objects.all():
        all_tag = all_tag + category_proc(obj)

    all_tag = list(set(all_tag))
    all_tag = sorted(all_tag)

    return all_tag


def fill_restaurant_context_info(search_result, search_text, page):
    context = {}

    context['restaurants'] = []
    context['categories'] = []
    context['query_rules'] = []
    context['rating'] = []
    context['last_search_text'] = search_text
    context['categories'] = get_all_tags()

    page_size = PAGESIZE_CONSTANT()
    result_num = len(search_result)
    page_num = math.ceil(result_num/page_size) + 1

    context['pages'] = range(1, page_num)
    context['page_size'] = page_size
    context['current_page'] = page

    #search_result = search_result[(page-1)*PAGESIZE_CONSTANT():page*PAGESIZE_CONSTANT()]
    for obj in search_result:
        restaurant = fill_restaurant_info(obj)
        context['restaurants'].append(restaurant)
        context['rating'].append(restaurant['rating'])

    if search_text != '':
        context['query_rules'].append(search_text)

    cache.set('context', context)

    return context


def page(request, page):
    context = {}
    search_result = cache.get('search_result')
    last_context = cache.get('context')
    if not search_result or not last_context:
        return render(request, 'groupbuying/search.html', context)

    if ('last_search_text' not in last_context or not last_context['last_search_text']):
        last_search_text = ''
    else:
        last_search_text = last_context['last_search_text']

    context = last_context
    context['current_page'] = page
    context['restaurants'] = context['restaurants'][(
        page-1)*PAGESIZE_CONSTANT():page*PAGESIZE_CONSTANT()]
    return render(request, 'groupbuying/search.html', context)


def fill_context_filter_query_rules(context, fitler_query):
    if fitler_query.rating != '':
        context['query_rules'].append(fitler_query.rating)

    for tag in fitler_query.tag:
        context['query_rules'].append(tag)

    cache.set('context', context)

    return context


def filtering(request):
    context = {}
    search_text = ''
    def fitler_query(): return 0
    if ('last_search_text' not in request.POST or not request.POST['last_search_text']):
        search_text = ''
    else:
        search_text = request.POST['last_search_text']

    if ('filter_last' in request.POST):
        result = search_text_proc(search_text)
    else:
        result = VendorInfo.objects.all()
        search_text = ''

    result = filter_by_price(request, result)
    result, fitler_query.rating = filter_by_rating(request, result)
    result, fitler_query.tag = filter_by_tag(request, result)

    context = fill_restaurant_context_info(result, search_text, 1)
    context = fill_context_filter_query_rules(context, fitler_query)
    context['restaurants'] = context['restaurants'][(
        0)*PAGESIZE_CONSTANT():1*PAGESIZE_CONSTANT()]
    cache.set('search_result', result)
    # cache.set('context',context)
    return render(request, 'groupbuying/search.html', context)


def filter_by_price(request, prev_result):
    if ('price_filter' in request.POST and request.POST['price_filter']):
        print('dummy\n')

    return prev_result


def filter_by_rating(request, prev_result):
    rating = -1
    rating_query = ''

    if ('star' not in request.POST
            or not request.POST['star']):
        return prev_result, rating_query

    star = request.POST['star']

    for i in range(0, 5):
        if (star == 'star' + str(i)):
            rating = i + 1
    if (rating == -1):
        return prev_result, rating_query

    avg_rating = Rating.objects.values('ratedTarget').annotate(
        avg_rating=Avg('rating')).order_by('ratedTarget')
    avg_rating_filtered = avg_rating.filter(rating__gte=rating)
    result = prev_result.filter(
        id__in=avg_rating_filtered.values('ratedTarget'))

    rating_query = "rating >=" + str(rating)
    return result, rating_query


def filter_by_tag(request, prev_result):
    all_tag = []
    fitler_tag = []

    result = VendorInfo.objects.none()
    all_tag = get_all_tags()

    for tag in all_tag:
        if tag in request.POST:
            fitler_tag.append(tag)

    if not fitler_tag:
        return prev_result, fitler_tag

    query = reduce(operator.or_,
                   (Q(tagList__contains=item) for item in fitler_tag))
    result = prev_result.filter(query)

    return result, fitler_tag


def sorting(request):
    context = {}

    search_result = cache.get('search_result')
    last_context = cache.get('context')
    if not search_result or not last_context:
        return render(request, 'groupbuying/search.html', context)

    if ('last_search_text' not in last_context or not last_context['last_search_text']):
        last_search_text = ''
    else:
        last_search_text = last_context['last_search_text']

    if ('sort_by_name' in request.POST):
        print('name\n')
        last_context['restaurants'] = sorted(last_context['restaurants'],
                                             key=lambda i: i['name'].lower())

    if ('sort_by_rating' in request.POST):
        print('rating\n')
        last_context['restaurants'] = sorted(last_context['restaurants'],
                                             key=lambda i: i['rating'],
                                             reverse=True)

    if ('sort_by_price' in request.POST):
        print('price\n')
        last_context = last_context

    cache.set('context', last_context)
    last_context['restaurants'] = last_context['restaurants'][0:PAGESIZE_CONSTANT()]

    return render(request, 'groupbuying/search.html', last_context)


def search_page(request):
    context = {}
    errors = []

    if request.method == 'GET':
        return render(request, 'groupbuying/search.html', context)

    if ('search_text' not in request.POST or not request.POST['search_text']):
        errors.append('Empty text. Please must enter restaurant info.')
        return render(request, 'groupbuying/search.html', context)

    search_result = search_text_proc(request.POST['search_text'])
    cache.set('search_result', search_result)
    page = 1
    context = fill_restaurant_context_info(search_result,
                                           request.POST['search_text'], page)

    context['restaurants'] = context['restaurants'][(
        0)*PAGESIZE_CONSTANT():1*PAGESIZE_CONSTANT()]
    # cache.set('context',context)
    return render(request, 'groupbuying/search.html', context)
    '''
    context['pages'] = range(1,10)
    context['current_page'] = 1
    context['categories'] = ['Drinks','Appetizer','Snack','Fast-food','Lunch','Dinner']
    context['restaurants'] = []
    restaurant1 = {
        'id': 1,
        'name': 'Starbucks',
        'description': 'Starbucks was established in 1971 by three local businessmen to sell high quality whole beans coffee. In 1981 when Howard Schultz visited the store he plan to build a strong company and expand high quality coffee business with the name of Starbucks.',
        'image': "https://upload.wikimedia.org/wikipedia/en/thumb/d/d3/Starbucks_Corporation_Logo_2011.svg/1200px-Starbucks_Corporation_Logo_2011.svg.png",
        'categories': ['Drinks','Snack'],
        'rating': 4,
        'price' : 5
    }
    restaurant2 = {
        'id': 2,
        'name': 'Pandas Express',
        'description': 'Panda Express is a fast food restaurant chain which serves American Chinese cuisine. With over 2,200 locations, it is the largest Asian segment restaurant chain in the United States, where it was founded and is mainly located (in addition to other countries and territories in North America and Asia).',
        'image': "https://upload.wikimedia.org/wikipedia/en/thumb/8/85/Panda_Express_logo.svg/1200px-Panda_Express_logo.svg.png",
        'categories': ['Lunch','Dinner'],
        'rating': 5,
        'price' : 12
    }
    restaurant3 = {
        'id': 3,
        'name': 'Mcdonald',
        'description': 'McDonalds.com is your hub for everything McDonald\'s. Find out more about our menu items and promotions today!',
        'image': "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/McDonald%27s_Golden_Arches.svg/1200px-McDonald%27s_Golden_Arches.svg.png",
        'categories': ['Fast-food'],
        'rating': 2,
        'price' : 7
    }
    context['restaurants'].append(restaurant1)
    context['restaurants'].append(restaurant2)
    context['restaurants'].append(restaurant3)
    return render(request, 'groupbuying/search.html',context)
    '''


def login_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'groupbuying/login.html', context)

    # Creates a bound form from the request POST parameters and makes the
    # form available in the request context dictionary.
    form = LoginForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'groupbuying/login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)
    return redirect(reverse('home'))


def logout_action(request):
    logout(request)
    return redirect(reverse('login'))


def register_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'groupbuying/register.html', context)

    # Creates a bound form from the request POST parameters and makes the
    # form available in the request context dictionary.
    form = RegistrationForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'groupbuying/register.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(
        username=form.cleaned_data['username'],
        password=form.cleaned_data['password'],
        email=form.cleaned_data['email'],
        first_name=form.cleaned_data['first_name'],
        last_name=form.cleaned_data['last_name'])
    new_user.save()

    new_customerInfo = CustomerInfo(name=form.cleaned_data['username'],
                                    email=form.cleaned_data['email'],
                                    description="Why nunu why",
                                    address=form.cleaned_data['address'],
                                    phoneNum=form.cleaned_data['cell_phone'],
                                    customer_id=request.user.id)
    new_customerInfo.save()

    new_vendorInfo = VendorInfo(name=form.cleaned_data['username'],
                                email=form.cleaned_data['email'],
                                description="test",
                                address=form.cleaned_data['address'],
                                phoneNum=form.cleaned_data['cell_phone'],
                                vendor_id=request.user.id)
    new_vendorInfo.save()

    new_userProfile = UserProfile(user=new_user,
                                  CustomerInfo=new_customerInfo,
                                  VendorInfo=new_vendorInfo)
    new_userProfile.save()

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)

    return redirect(reverse('home'))
