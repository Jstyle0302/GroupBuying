import json
import operator
import math
import random
import datetime
import re

from collections import defaultdict
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.urls import reverse
from django.http import HttpResponse, Http404
from django.http import HttpResponseForbidden
from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.utils.timezone import is_aware, make_aware
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.cache import cache

from groupbuying.forms import LoginForm, RegistrationForm, ProductForm, VendorInfoForm, CustomerInfoForm
from groupbuying.models import Product, CustomerInfo, VendorInfo, Rating, UserProfile, OrderUnit, OrderBundle, Category, Statistic
from django.db.models import Q
from django.db.models import Avg
from functools import reduce
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def PAGESIZE_CONSTANT():
    return 5


def handler404(request, *args, **argv):
    context = {}

    return render(request, 'groupbuying/404.html', context)


def handler500(request, *args, **argv):
    return render(request, 'groupbuying/404.html')


def home_page(request):
    context = {}

    search_result = search_text_proc("")
    context['restaurants'] = []
    context['categories'] = []
    context['query_rules'] = []
    context['rating'] = []
    context['categories'] = get_all_tags()

    for obj in search_result:
        restaurant = fill_restaurant_info(obj)
        context['restaurants'].append(restaurant)
        context['rating'].append(restaurant['rating'])

    context['restaurants'] = sorted(context['restaurants'],
                                    key=lambda i: i['rating'],
                                    reverse=True)

    context['recommends'] = []
    dict_recommand = {}
    i = 0
    for obj in context['restaurants']:
        if i >= 3:
            break
        dict_recommand = {
            'id': obj['id'],
            'name': obj['name'],
            'description': obj['description'],
            'image': obj['image']
        }
        context['recommends'].append(dict_recommand)
        i += 1

    return render(request, 'groupbuying/home.html', context)


@login_required
def orderList_page(request):
    context = {}
    customerInfo = CustomerInfo.objects.filter(Q(id=str(request.user.id)))[0]
    orderUnits = OrderUnit.objects.filter(Q(buyer=customerInfo))
    orderBundles = OrderBundle.objects.filter(Q(customer=customerInfo))

    context['orders'] = []
    for orderBundle in orderBundles:
        if orderBundle.isPaid == True:
            continue

        order = {
            'order_id': orderBundle.id,
            'name': orderBundle.vendor.name,
            'description': orderBundle.vendor.description
        }

        if orderBundle.vendor.image:
            order['image'] = orderBundle.vendor.image.url
        else:
            order['image'] = orderBundle.vendor.image_url_OAuth

        context['orders'].append(order)

    return render(request, 'groupbuying/orderList.html', context)


@login_required
def share_page(request, order_id):
    context = {}
    context = {}
    orderbundle = OrderBundle.objects.filter(Q(id=str(order_id)))[0]
    shop_id = orderbundle.vendor.id
    context = get_shopPage_context(request, shop_id)

    context['founder'] = orderbundle.holder.name
    context['order_id'] = order_id

    return render(request, 'groupbuying/shop.html', context)


@login_required
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
        total_price += float(orderUnit.product.price)*int(orderUnit.quantity)
        dictOrder['order'] = []
        subOrder = {
            'product': orderUnit.product.name,
            'count': orderUnit.quantity,
            'price': orderUnit.product.price
        }
        dictOrder['order'].append(subOrder)
        context['receipt']['orders'].append(dictOrder)

    context['receipt']['summary']['total'] = total_price

    subject = str(request.user.username) + "'s order at " + \
        orderbundle.vendor.name + "(order_id:" + str(orderbundle.id) + ")"
    html_message = render_to_string('groupbuying/order_email.html', context)
    plain_message = strip_tags(html_message)
    from_email = 'groupbuyingTeam23@gmail.com'
    to_email = [request.user.email]

    send_mail(subject, plain_message, from_email, to_email,
              html_message=html_message, fail_silently=False)

    return redirect('shop')


@login_required
def remove_orderUnit(request, order_unit_id):
    context = {}
    toBeRemoved_orderUnit = OrderUnit.objects.filter(Q(id=str(order_unit_id)))
    if not toBeRemoved_orderUnit:
        return redirect('home')

    toBeRemoved_orderUnit = toBeRemoved_orderUnit[0]
    orderbundle = toBeRemoved_orderUnit.orderbundle
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
    context['min_order'] = orderbundle.vendor.min_order

    for orderUnit in orderUnits:
        if orderUnit == toBeRemoved_orderUnit:
            continue
        dictOrder = {}
        dictOrder['username'] = (orderUnit.buyer.name)
        dictOrder['userid'] = (orderUnit.buyer.id)
        dictOrder['order'] = []
        dictOrder['description'] = orderUnit.comment
        dictOrder['orderUnitId'] = orderUnit.id
        subOrder = {
            'product': orderUnit.product.name,
            'count': orderUnit.quantity,
            'price': orderUnit.product.price,
        }
        dictOrder['total'] = int(orderUnit.quantity) * \
            float(orderUnit.product.price)

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
                order['count'] = str(
                    int(order['count']) + int(orderUnit.quantity))

        if is_product_exist == 0:
            context['receipt']['summary']['order'].append(summary)

    total_price = 0

    for order in context['receipt']['summary']['order']:
        order['price'] = (int(order['count']) * int(order['price']))
        total_price += order['price']

    context['receipt']['summary']['total'] = total_price

    toBeRemoved_orderUnit.delete()

    return render(request, 'groupbuying/order.html', context)


@login_required
def show_order_page(request, order_id, from_profile):
    context = {}
    orderbundle = OrderBundle.objects.filter(Q(id=str(order_id)))
    if not orderbundle:
        return redirect('home')

    orderbundle = orderbundle[0]

    if (orderbundle.isPaid == True) and (int(from_profile) != 1):
        return redirect('home')

    customerInfo = CustomerInfo.objects.filter(Q(id=str(request.user.id)))[0]

    if int(from_profile) == 1:
        context['from_profile'] = 1

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
    context['min_order'] = orderbundle.vendor.min_order

    for orderUnit in orderUnits:
        dictOrder = {}
        dictOrder['username'] = (orderUnit.buyer.name)
        dictOrder['order'] = []
        dictOrder['description'] = orderUnit.comment
        dictOrder['userid'] = (orderUnit.buyer.id)
        dictOrder['orderUnitId'] = orderUnit.id
        subOrder = {
            'product': orderUnit.product.name,
            'count': orderUnit.quantity,
            'price': orderUnit.product.price,
        }
        dictOrder['total'] = int(orderUnit.quantity) * \
            float(orderUnit.product.price)

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
                order['count'] = str(
                    int(order['count']) + int(orderUnit.quantity))

        if is_product_exist == 0:
            context['receipt']['summary']['order'].append(summary)

    total_price = 0

    for order in context['receipt']['summary']['order']:
        order['price'] = (int(order['count']) * float(order['price']))
        total_price += order['price']

    context['receipt']['summary']['total'] = total_price

    return render(request, 'groupbuying/order.html', context)


@login_required
def order_page(request, order_id):
    context = {}
    if 'product_id' not in request.POST or not request.POST['product_id'] or \
            'product_number' not in request.POST or not request.POST['product_number']:
        return redirect('home')

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
        comment='',
        orderTime=datetime.datetime.now(),
        orderDate=datetime.datetime.now(),
        deliverTime=datetime.datetime.now(),
        deliverDate=datetime.datetime.now(),
        isPaid=True,
        orderbundle=new_orderbundle
    )
    new_orderUnit.save()

    new_orderbundle.customer.add(customerInfo)
    orderbundle = new_orderbundle

    if orderbundle.holder.id == request.user.id:
        context['isFounder'] = True
        orderUnits = OrderUnit.objects.filter(Q(orderbundle=orderbundle))

    else:
        context['isFounder'] = False
        orderUnits = OrderUnit.objects.filter(
            Q(buyer=customerInfo) & Q(orderbundle=orderbundle))

    context['receipt'] = {}
    context['receipt']['orders'] = []
    context['receipt']['summary'] = {}
    context['receipt']['summary']['order'] = []
    context['min_order'] = orderbundle.vendor.min_order

    for orderUnit in orderUnits:
        dictOrder = {}
        dictOrder['username'] = (orderUnit.buyer.name)
        dictOrder['order'] = []
        dictOrder['description'] = orderUnit.comment
        dictOrder['userid'] = (orderUnit.buyer.id)
        dictOrder['orderUnitId'] = orderUnit.id
        subOrder = {
            'product': orderUnit.product.name,
            'count': orderUnit.quantity,
            'price': orderUnit.product.price,
        }
        dictOrder['total'] = int(orderUnit.quantity) * \
            float(orderUnit.product.price)

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
                order['count'] = str(
                    int(order['count']) + int(orderUnit.quantity))

        if is_product_exist == 0:
            context['receipt']['summary']['order'].append(summary)

    total_price = 0

    for order in context['receipt']['summary']['order']:
        order['price'] = (int(order['count']) * float(order['price']))
        total_price += order['price']

    context['receipt']['summary']['total'] = total_price

    context['checkout_to_holder'] = 1
    context['order_id'] = new_orderbundle.id
    context['order_unit_id'] = new_orderUnit.id
    context['shop'] = vendorInfo.name
    context['founder'] = new_orderbundle.holder.name

    return render(request, 'groupbuying/order.html', context)


@login_required
def checkout_to_holder(request, order_unit_id):
    context = {}
    orderUnit = OrderUnit.objects.filter(Q(id=str(order_unit_id)))[0]
    if 'orderDescription' in request.POST and request.POST['orderDescription']:
        orderUnit.comment = request.POST['orderDescription']

    orderUnit.isPaid = True
    orderUnit.save()

    return redirect('home')


@login_required
def delete_orderbundle(request, order_id):
    context = {}
    orderbundle = OrderBundle.objects.filter(Q(id=str(order_id)))[0]
    orderUnits = OrderUnit.objects.filter(Q(orderbundle=orderbundle))

    for orderUnit in orderUnits:
        orderUnit.delete()

    orderbundle.delete()

    return redirect('home')


@login_required
def checkout_to_shopper(request, order_id):
    context = {}
    orderbundle = OrderBundle.objects.filter(Q(id=str(order_id)))[0]
    customerInfo = CustomerInfo.objects.filter(Q(id=str(request.user.id)))[0]
    orderbundle.isPaid = True
    orderbundle.save()

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
        dictOrder['total'] = int(orderUnit.quantity) * \
            float(orderUnit.product.price)

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
                order['count'] = str(
                    int(order['count']) + int(orderUnit.quantity))

        if is_product_exist == 0:
            context['receipt']['summary']['order'].append(summary)

    total_price = 0

    for order in context['receipt']['summary']['order']:
        order['price'] = (int(order['count']) * float(order['price']))
        total_price += order['price']

    context['receipt']['summary']['total'] = total_price
    orderbundle.totalPrice = total_price
    orderbundle.save()

    subject = str(request.user.username) + "'s order at " + \
        orderbundle.vendor.name + "(order_id:" + str(orderbundle.id) + ")"
    html_message = render_to_string('groupbuying/order_email.html', context)
    plain_message = strip_tags(html_message)
    from_email = 'groupbuyingTeam23@gmail.com'
    vendor_user = User.objects.filter(Q(id=str(orderbundle.vendor.id)))[0]
    to_email = [request.user.email, vendor_user.email]

    send_mail(subject, plain_message, from_email, to_email,
              html_message=html_message, fail_silently=False)

    return redirect('home')


def gen_context_profile(customerInfo):
    context = {}
    context['username'] = customerInfo.name
    context['description'] = customerInfo.description
    OrderUnits = OrderUnit.objects.filter(Q(buyer=customerInfo))

    context['orders'] = []
    i = 0
    orderbundle_id_list = []

    for orderUnit in reversed(OrderUnits):
        if i >= 5 or orderUnit.orderbundle.id in orderbundle_id_list:
            break

        order = {}
        order['shop_name'] = orderUnit.orderbundle.vendor.name
        order['orderbundle_id'] = orderUnit.orderbundle.id
        orderbundle_id_list.append(orderUnit.orderbundle.id)

        context['orders'].append(order)
        i += 1

    context['subcribes'] = []
    for favoriteVendor in customerInfo.subscription.all():
        subcribes = {}
        subcribes['shop_name'] = (favoriteVendor.name)
        subcribes['shop_id'] = (favoriteVendor.id)
        context['subcribes'].append(subcribes)

    context['customerInfo'] = customerInfo
    return context


@login_required
def add_to_favorite(request, shop_id):
    context = {}
    customerInfo = CustomerInfo.objects.filter(Q(id=str(request.user.id)))[0]
    vendor = VendorInfo.objects.filter(Q(id=str(shop_id)))[0]
    customerInfo.subscription.add(vendor)
    customerInfo.save()

    context = gen_context_profile(customerInfo)

    return render(request, 'groupbuying/profile.html', context)


@login_required
def remove_from_favorite(request, shop_id):
    context = {}
    customerInfo = CustomerInfo.objects.filter(Q(id=str(request.user.id)))[0]
    vendor = VendorInfo.objects.filter(Q(id=str(shop_id)))[0]
    customerInfo.subscription.remove(vendor)
    customerInfo.save()

    context = gen_context_profile(customerInfo)

    return render(request, 'groupbuying/profile.html', context)


@login_required
def profile_page(request, user_id):
    context = {}
    customerInfo = CustomerInfo.objects.filter(Q(id=str(user_id)))[0]
    context = gen_context_profile(customerInfo)

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


def delete_tag(request, tag_name):
    errors = []  # A list to record messages for any errors we encounter.
    cur_vendor_info = get_object_or_404(VendorInfo, vendor_id=request.user.id)

    old_tag_list = re.split('[\*\,\/\+\s]', cur_vendor_info.tagList)
    new_tag_list = [tag for tag in old_tag_list if tag != tag_name]
    cur_vendor_info.tagList = str(','.join(new_tag_list))
    cur_vendor_info.save()

    return redirect('shop_edit')


def get_menu(vendor_id):
    menu = {}
    categories = Category.objects.filter(vendor__id=vendor_id)
    categories_names = [obj.name for obj in categories]

    for name in categories_names:
        temp_dish_dict = {}
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

        temp_dish_dict['dishes'] = dict(temp_pdict)
        temp_dish_dict['id'] = categories.get(name=name).id
        menu[name] = dict(temp_dish_dict)

    return menu


def get_product_sales(order_bundle_id, pre_json):
    # load prev_json data as dict
    product_sale_dict = {}
    if pre_json != None:
        product_sale_dict = pre_json

    # value: str -> float
    for key in product_sale_dict:
        product_sale_dict[key] = float(product_sale_dict[key])

    # update json data
    cur_order = get_object_or_404(OrderBundle, pk=int(order_bundle_id))

    cur_order_units = OrderUnit.objects.filter(orderbundle=cur_order)
    for order in cur_order_units:
        if order.product.name in product_sale_dict:
            product_sale_dict[order.product.name] += float(
                order.quantity) * float(order.product.price)
        else:
            product_sale_dict[order.product.name] = float(
                order.quantity) * float(order.product.price)

    return dict(product_sale_dict)


def get_statistic_json(request):
    cur_time = datetime.datetime.now()
    response_text = serializers.serialize('json', Statistic.objects.all().filter(
        year=cur_time.year, vendor__id=request.user.id))

    return HttpResponse(response_text, content_type='application/json')


def get_orders(vendor_id):
    incompleted = []
    finished = []

    orderbundles = OrderBundle.objects.filter(vendor__id=vendor_id)

    for orderbundle in orderbundles:
        if orderbundle.isPaid:
            tmp_order = {'order': []}
            tmp_summary = {}
            tmp_orderbundle_dict = {'order_id': orderbundle.id}
            orderUnits = OrderUnit.objects.filter(orderbundle=orderbundle)

            for orderUnit in orderUnits:
                tmp_orderUnit_dict = {}
                tmp_orderUnit_dict['product'] = orderUnit.product.name
                tmp_orderUnit_dict['count'] = orderUnit.quantity
                tmp_orderUnit_dict['price'] = orderUnit.product.price
                tmp_order['order'].append(dict(tmp_orderUnit_dict))

            tmp_summary['summary'] = dict(tmp_order)
            tmp_orderbundle_dict['receipt'] = dict(tmp_summary)

            tmp_orderbundle_dict['receipt']['summary']['total'] = orderbundle.totalPrice
            if orderbundle.isCompleted:
                finished.append(dict(tmp_orderbundle_dict))
            else:
                incompleted.append(dict(tmp_orderbundle_dict))

    return incompleted, finished


def get_reviews(vendor_id):
    posts = []
    ratings = Rating.objects.filter(ratedTarget__id=vendor_id)

    for rating in ratings:
        tmp_review_dict = {}
        tmp_review_dict['id'] = rating.id
        tmp_review_dict['created_by'] = {'username': rating.rater.name}
        tmp_review_dict['creation_time'] = rating.createTime
        tmp_review_dict['creation_date'] = rating.createDate
        tmp_review_dict['post'] = rating.comment
        tmp_review_dict['rating'] = rating.rating
        posts.append(dict(tmp_review_dict))

    return posts


def get_shopPage_context(request, shop_id):
    context = {}
    cur_vendor_info = get_object_or_404(VendorInfo, vendor_id=shop_id)

    context['menu'] = get_menu(cur_vendor_info.vendor_id)
    context['posts'] = get_reviews(cur_vendor_info.vendor_id)

    tag_re = re.split('[\*\,\/\+\s]', cur_vendor_info.tagList)
    if tag_re[0] != '':
        tag_re = [tag for tag in tag_re if tag != '']
        context['tags'] = tag_re

    context['incompleted'], context['finished'] = get_orders(
        cur_vendor_info.vendor_id)
    context['vendorInfo'] = cur_vendor_info

    if request.user.id:
        is_subscribe = CustomerInfo.objects.filter(Q(id=str(request.user.id)) &
                                                   Q(subscription=cur_vendor_info))

        if is_subscribe:
            context['is_subscribe'] = 1
        else:
            context['is_subscribe'] = 0

    return context


def get_shopEditPage_context(request):
    context = {}
    cur_vendor_info = get_object_or_404(VendorInfo, pk=request.user.id)

    context['menu'] = get_menu(cur_vendor_info.vendor_id)
    context['posts'] = get_reviews(cur_vendor_info.vendor_id)

    tag_re = re.split('[\*\,\/\+\s]', cur_vendor_info.tagList)
    if tag_re[0] != '':
        tag_re = [tag for tag in tag_re if tag != '']
        context['tags'] = tag_re

    context['incompleted'], context['finished'] = get_orders(
        cur_vendor_info.vendor_id)
    context['productForm'] = ProductForm()
    context['vendorInfo'] = cur_vendor_info
    context['vendorForm'] = VendorInfoForm(
        initial={'description': cur_vendor_info.description}, instance=cur_vendor_info)

    return context


@login_required
def shopEdit_page(request):
    context = {}
    context = get_shopEditPage_context(request)

    return render(request, 'groupbuying/shopEdit.html', context)


def shop_page(request, shop_id):
    context = {}
    context = get_shopPage_context(request, shop_id)

    return render(request, 'groupbuying/shop.html', context)


def random_shop(request):
    total_shops_num = len(VendorInfo.objects.all())
    shop_id = random.randint(1, total_shops_num)

    return redirect('shop/' + str(shop_id))


@login_required
def complete_order(request):
    errors = []
    cur_order = None
    if 'order_id' not in request.POST or not request.POST['order_id']:
        errors.append('You must have provide the order id')
        return HttpResponseRedirect(reverse('shop_edit') + "#list-orders")

    cur_order = get_object_or_404(
        OrderBundle, pk=int(request.POST['order_id']))
    cur_order.isCompleted = True
    cur_order.save()

    # Add total sales to statistic
    cur_time = datetime.datetime.now()
    cur_statistic = Statistic.objects.filter(
        year=cur_time.year, month=cur_time.month, vendor__id=request.user.id)

    if len(cur_statistic) > 0:
        cur_statistic[0].sales += cur_order.totalPrice
        cur_statistic[0].productSales = get_product_sales(
            request.POST['order_id'], cur_statistic[0].productSales)
        cur_statistic[0].save()
    else:
        new_statistic = Statistic(year=cur_time.year,
                                  month=cur_time.month,
                                  sales=cur_order.totalPrice,
                                  expense=0,
                                  productSales=get_product_sales(
                                      request.POST['order_id'], None),
                                  vendor=cur_order.vendor)
        new_statistic.save()

    holder_user = User.objects.filter(Q(id=str(cur_order.vendor.id)))[0]
    subject = str(holder_user.username) + "'s order at " + \
        cur_order.vendor.name + \
        "(order_id:" + str(cur_order.id) + ") is completed"
    context = {}
    context['order_completed'] = 1
    context['founder'] = holder_user.username
    html_message = render_to_string('groupbuying/order_email.html', context)
    plain_message = strip_tags(html_message)
    from_email = 'groupbuyingTeam23@gmail.com'
    to_email = [holder_user.email]

    send_mail(subject, plain_message, from_email, to_email,
              html_message=html_message, fail_silently=False)

    return HttpResponseRedirect(reverse('shop_edit') + "#list-orders")


@login_required
def update_category_name(request):
    errors = []  # A list to record messages for any errors we encounter.
    cur_vendor_info = get_object_or_404(VendorInfo, vendor_id=request.user.id)

    if 'new_menu_name' not in request.POST or not request.POST['new_menu_name']:
        errors.append('You must have enter the new_menu name')
        return redirect('shop_edit')

    if 'menu_id' not in request.POST or not request.POST['menu_id']:
        errors.append('You must provide menu id')
        return redirect('shop_edit')

    cur_category = Category.objects.filter(
        pk=int(request.POST['menu_id']))[0]
    cur_category.name = request.POST['new_menu_name']
    cur_category.save()

    target_list = "#list-menu-" + \
        str(request.POST['new_menu_name'].replace(" ", ""))

    return HttpResponseRedirect(reverse('shop_edit') + target_list)


@login_required
def add_category(request):
    errors = []  # A list to record messages for any errors we encounter.

    # Adds the new item to the database if the request parameter is present
    if 'new_category' not in request.POST or not request.POST['new_category']:
        errors.append('You must enter text to add new category.')
        return redirect('shop_edit')

    new_category = Category(name=request.POST['new_category'],
                            vendor=request.user)
    new_category.save()
    target_list = "#list-menu-" + \
        str(request.POST['new_category'].replace(" ", ""))

    return HttpResponseRedirect(reverse('shop_edit') + target_list)


@login_required
def get_product_photo(request, product_id):
    product = get_object_or_404(Product, pk=str(product_id))
    if not product.image:
        print("Cannot find photo")
        raise Http404

    return HttpResponse(product.image, content_type=product.content_type)


@login_required
def add_product(request):
    errors = []  # A list to record messages for any errors we encounter.

    if 'name' not in request.POST or not request.POST['name'] or \
            'price' not in request.POST or not request.POST['price']:
        errors.append(
            'You must have at least "name and price" for the product')
        return redirect('shop_edit')

    if 'description' not in request.POST or 'price' not in request.POST or \
            'current_category' not in request.POST:
        errors.append('description or price NOT in form data')
        return redirect('shop_edit')

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
    if form.is_valid():
        if 'image' in request.FILES:
            new_product.image = form.cleaned_data['image']
            new_product.content_type = form.cleaned_data['image'].content_type
        form.save()

    target_list = "#list-menu-" + \
        str(request.POST['current_category'].replace(" ", ""))

    return HttpResponseRedirect(reverse('shop_edit') + target_list)


@login_required
def update_product(request):
    errors = []  # A list to record messages for any errors we encounter.
    if 'name' not in request.POST or not request.POST['name'] or \
            'price' not in request.POST or not request.POST['price']:
        errors.append(
            'You must have at least "name and price" for the product')
        return redirect('shop_edit')

    if 'product_id' not in request.POST or 'description' not in request.POST:
        errors.append('product_id or description NOT in the form data')
        return redirect('shop_edit')

    cur_product = get_object_or_404(
        Product, pk=int(request.POST['product_id']))

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

    target_list = "#list-menu-" + (cur_product.category.name).replace(" ", "")

    return HttpResponseRedirect(reverse('shop_edit') + target_list)


@login_required
def update_vendor_name(request):
    errors = []  # A list to record messages for any errors we encounter.
    cur_vendor_info = get_object_or_404(VendorInfo, vendor_id=request.user.id)

    if 'vendor_name' not in request.POST or not request.POST['vendor_name']:
        errors.append('You must have enter the vendor name')
        return redirect('shop_edit')

    cur_vendor_info.name = request.POST['vendor_name']
    cur_vendor_info.save()

    return HttpResponseRedirect(reverse('shop_edit') + "#list-profile")


@login_required
def update_vendor_info(request):
    errors = []  # A list to record messages for any errors we encounter.
    cur_vendor_info = get_object_or_404(VendorInfo, vendor_id=request.user.id)

    form = VendorInfoForm(request.POST, request.FILES,
                          instance=cur_vendor_info)
    if not form.is_valid():
        print("FALI: form is NOT valid")
    else:
        if 'description' in request.POST and request.POST['description']:
            cur_vendor_info.description = request.POST['description']
        if 'min_order' in request.POST and request.POST['min_order']:
            cur_vendor_info.min_order = int(request.POST['min_order'])
        if 'image' in request.FILES:
            cur_vendor_info.image = form.cleaned_data['image']
            cur_vendor_info.content_type = form.cleaned_data['image'].content_type

        form.save()

    return HttpResponseRedirect(reverse('shop_edit') + "#list-profile")


@login_required
def rating_star(request):
    rating = ''
    if 'shop_id' in request.POST and request.POST['shop_id']:
        target_info = get_object_or_404(
            VendorInfo, pk=int(request.POST['shop_id']))
    else:
        return redirect('shop/' + '1')

    if 'rating' in request.POST and request.POST['rating']:
        rating = request.POST['rating']
    else:
        return redirect('shop/' + str(request.POST['shop_id']))

    if 'comment' not in request.POST:
        return redirect('shop/' + str(request.POST['shop_id']))

    customer_info = CustomerInfo.objects.filter(
        id=str(request.user.id)).first()

    old_rating = Rating.objects.filter(Q(rater=customer_info) & Q(
        ratedTarget=target_info)).first()

    if not old_rating:
        new_rating = Rating(rating=float(rating),
                            comment=request.POST['comment'],
                            createTime=datetime.datetime.now(),
                            createDate=datetime.datetime.now(),
                            rater=customer_info,
                            ratedTarget=target_info)
        new_rating.save()
    else:
        old_rating.rating = float(rating)
        old_rating.comment = request.POST['comment']
        old_rating.createTime = datetime.datetime.now()
        old_rating.createDate = datetime.datetime.now()
        old_rating.save()

    return redirect('shop/' + request.POST['shop_id'] + "#list-review")


@login_required
def update_customer_info(request, user_id):
    context = {}
    errors = []
    cur_customer_info = CustomerInfo.objects.filter(id=str(user_id)).first()

    if 'description' in request.POST and request.POST['description']:
        cur_customer_info.description = request.POST['description']
        form = CustomerInfoForm(
            request.POST, request.FILES, instance=cur_customer_info)
        if form.is_valid():
            print("form is valid 1")
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

    context = gen_context_profile(cur_customer_info)
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
    if search_text == "":
        search_result = VendorInfo.objects.all()
    else:
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

    if not obj.min_order:
        restaurant['price'] = 0
    else:
        restaurant['price'] = obj.min_order

    if obj.image:
        restaurant['image'] = obj.image.url
    else:
        restaurant['image'] = obj.image_url_OAuth

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

    if fitler_query.price != '':
        context['query_rules'].append(fitler_query.price)

    cache.set('context', context)

    return context

def filtering_chatbot(request):
    context = {}
    search_text = ''
    if request.method == 'POST':
        return redirect(reverse('home'))

    def fitler_query(): return 0

    result = VendorInfo.objects.all()

    result, fitler_query.price = filter_by_price(request, result)
    result, fitler_query.tag = filter_by_tag(request, result)
    fitler_query.rating = ''

    context = fill_restaurant_context_info(result, search_text, 1)
    context = fill_context_filter_query_rules(context, fitler_query)
    context['restaurants'] = context['restaurants'][(
        0)*PAGESIZE_CONSTANT():1*PAGESIZE_CONSTANT()]
    cache.set('search_result', result)

    return render(request, 'groupbuying/search.html', context)

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

    result, fitler_query.price = filter_by_price(request, result)
    result, fitler_query.rating = filter_by_rating(request, result)
    result, fitler_query.tag = filter_by_tag(request, result)

    context = fill_restaurant_context_info(result, search_text, 1)
    context = fill_context_filter_query_rules(context, fitler_query)
    context['restaurants'] = context['restaurants'][(
        0)*PAGESIZE_CONSTANT():1*PAGESIZE_CONSTANT()]
    cache.set('search_result', result)

    return render(request, 'groupbuying/search.html', context)


def filter_by_price(request, prev_result):
    price_query = ''
    if (request.method == 'POST' and ('price_filter' not in request.POST
            or not request.POST['price_filter'])):
        return prev_result, price_query
    if (request.method == 'GET' and ('price_filter' not in request.GET
            or not request.GET['price_filter'])):
        return prev_result, price_query

    if request.method == 'POST' and str(request.POST['price_filter']).isnumeric():
        price = int(request.POST['price_filter'])
    elif request.method == 'GET' and str(request.GET['price_filter']).isnumeric():
        price = int(request.GET['price_filter'])
    else:
        price = 0

    if price < 100:
        result = prev_result.filter(
            min_order__lte=price)
    else:
        result = prev_result

    for obj in prev_result:
        if not obj.min_order:
            result |= VendorInfo.objects.filter(id=obj.id)

    price_query = "price <= " + str(price)

    return result, price_query


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

    for obj in prev_result:
        if not avg_rating.filter(ratedTarget=int(obj.id)) and int(rating) <= 3:
            result |= VendorInfo.objects.filter(id=obj.id)

    rating_query = "rating >= " + str(rating)
    return result, rating_query


def filter_by_tag(request, prev_result):
    all_tag = []
    fitler_tag = []

    result = VendorInfo.objects.none()
    all_tag = get_all_tags()

    if (request.method == 'POST'):
        for tag in all_tag:
            if tag in request.POST:
                fitler_tag.append(tag)
    elif (request.method == 'GET'):
        for tag in all_tag:
            if tag in request.GET:
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
        last_context['restaurants'] = sorted(last_context['restaurants'],
                                             key=lambda i: i['name'].lower())

    if ('sort_by_rating' in request.POST):
        last_context['restaurants'] = sorted(last_context['restaurants'],
                                             key=lambda i: i['rating'],
                                             reverse=True)

    if ('sort_by_price' in request.POST):
        last_context['restaurants'] = sorted(last_context['restaurants'],
                                             key=lambda i: i['price'])

    cache.set('context', last_context)
    last_context['restaurants'] = last_context['restaurants'][0:PAGESIZE_CONSTANT()]

    return render(request, 'groupbuying/search.html', last_context)


def search_page(request):
    context = {}
    errors = []
    
    if request.method == 'GET' and 'search_text' in request.GET:
        search_text = request.GET['search_text']
    elif request.method == 'GET' and 'search_text' not in request.GET:    
        search_text = ""
    elif request.method == 'POST' and ('search_text' not in request.POST):
        errors.append('Empty text. Please must enter restaurant info.')
        return render(request, 'groupbuying/search.html', context)
    else :
        search_text = request.POST['search_text']

    
    search_result = search_text_proc(search_text)
    cache.set('search_result', search_result)
    page = 1
    context = fill_restaurant_context_info(search_result,
                                           search_text, page)

    context['restaurants'] = context['restaurants'][(
        0)*PAGESIZE_CONSTANT():1*PAGESIZE_CONSTANT()]
    # cache.set('context',context)
    return render(request, 'groupbuying/search.html', context)


def login_action(request):
    context = {}

    if request.user.is_authenticated:
        return redirect(reverse('home'))
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

    if request.user.is_authenticated:
        return redirect(reverse('home'))
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
                                    customer_id=new_user.id)
    new_customerInfo.save()

    new_vendorInfo = VendorInfo(name=form.cleaned_data['username'],
                                email=form.cleaned_data['email'],
                                description="test",
                                address=form.cleaned_data['address'],
                                phoneNum=form.cleaned_data['cell_phone'],
                                vendor_id=new_user.id)

    new_vendorInfo.save()

    new_userProfile = UserProfile(user=new_user,
                                  CustomerInfo=new_customerInfo,
                                  VendorInfo=new_vendorInfo)
    new_userProfile.save()

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)

    return redirect(reverse('home'))
