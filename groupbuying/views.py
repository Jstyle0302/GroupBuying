import json
import operator

from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.urls import reverse
from django.http import HttpResponse, Http404
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.utils.timezone import is_aware, make_aware
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import ensure_csrf_cookie

from groupbuying.forms import LoginForm, RegistrationForm, ProductForm, ImageUploadForm
from groupbuying.models import Product, CustomerInfo, VendorInfo, Rating, UserProfile, OrderUnit, OrderBundle, Category
from django.db.models import Q
from django.db.models import Avg
from functools import reduce

# @ensure_csrf_cookie
# @login_required

def home_page(request):
    context = {}
    return render(request, 'groupbuying/home.html', context)

<<<<<<< Updated upstream
def profile_page(request):
    context = {}
    context['username'] = 'Jeff'
    context['description'] = 'Amazing!'
    context['orders'] = ['Pizza Hut', 'Cold Stone', 'Jeff']
    context['followers'] = ['Shine','Charles','Ari','En-ting','Ting']
    context['subcribes'] = ['Starbucks','Pandas','Subway']
    context['photo'] = "https://cdn.business2community.com/wp-content/uploads/2017/08/blank-profile-picture-973460_640.png"
    return render(request, 'groupbuying/profile.html', context)

def other_page(request):
    context = {}
    context['username'] = 'Jeff'
    context['description'] = 'Amazing!'
    context['orders'] = ['Pizza Hut', 'Cold Stone', 'Jeff']
    context['followers'] = ['Shine','Charles','Ari','En-ting','Ting']
    context['subcribes'] = ['Starbucks','Pandas','Subway']
    context['photo'] = "https://cdn.business2community.com/wp-content/uploads/2017/08/blank-profile-picture-973460_640.png"
    return render(request, 'groupbuying/others.html', context)

=======
@login_required
>>>>>>> Stashed changes
def shop_page(request):
    context = {}
    context['form'] = ProductForm()
    context['shop_name'] = "Starbucks"
    context['description'] = "Very expensive and unhealthy food."
    context['logo'] = "https://upload.wikimedia.org/wikipedia/en/thumb/d/d3/Starbucks_Corporation_Logo_2011.svg/1200px-Starbucks_Corporation_Logo_2011.svg.png"
    context['menu'] = {
        'Coffee': {
            'Cappuccino': {
                'price': 5,
                'image': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/A_small_cup_of_coffee.JPG/1200px-A_small_cup_of_coffee.JPG',
                'description': 'Outside Greece and Cyprus, Freddo Cappucino or Cappuccino Freddo is mostly found in coffee shops and delis catering to the Greek expat community.'
            },
            'Cold brew': {
                'price': 6,
                'image': 'https://media3.s-nbcnews.com/j/newscms/2019_33/2203981/171026-better-coffee-boost-se-329p_67dfb6820f7d3898b5486975903c2e51.fit-760w.jpg',
                'description': 'It\'s more mellow and less acidic than hot and iced coffee; You get a slow release caffeine hit when compared to hot brewed coffee.'
            }
        },
        'Tea': {
            'Green Tea': {
                'price': 4,
                'image': 'https://i0.wp.com/images-prod.healthline.com/hlcmsresource/images/AN_images/green-tea-white-mug-1296x728.jpg?w=1155&h=1528',
                'description': 'It\'s more mellow and less acidic than hot and iced coffee; You get a slow release caffeine hit when compared to hot brewed coffee.'
            },
            'Chai Latte': {
                'price': 4.5,
                'image': 'https://globalassets.starbucks.com/assets/b635f407bbcd49e7b8dd9119ce33f76e.jpg?impolicy=1by1_wide_1242',
                'description': 'Outside Greece and Cyprus, Freddo Cappucino or Cappuccino Freddo is mostly found in coffee shops and delis catering to the Greek expat community.'
            }
        }
    }

    context['categories'] = Category.objects.all()
    context['products'] = Product.objects.all()
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

    context['categories'] = Category.objects.all()
    context['products'] = Product.objects.all()
    context['errors'] = errors
    # context = {'categories': Category.objects.all(), 'products': Product.objects.all(), 'errors': errors}

    return render(request, 'groupbuying/shop.html', context)

@login_required
def add_product(request):
    context = {}
    errors = []  # A list to record messages for any errors we encounter.
    form = None

    if 'name' not in request.POST or not request.POST['name'] or \
        'price' not in request.POST or not request.POST['price']:
        errors.append('You must have at least "name and price" for the product')
    else:
        new_product = Product(name=str(request.POST['name']),
                              description=str(request.POST['description']),
                              price=float(request.POST['price']),
                              sellerId=str(request.user.id),
                              isAvailable=True,
                              saleVolume=0,
                              vendor=request.user,
                              category=Category.objects.filter(name=request.POST['current_category'])[0])

        form = ProductForm(request.POST, request.FILES, instance=new_product)
        # form = ImageUploadForm(request.POST, request.FILES)

        if not form.is_valid():
            # print("form is NOT valid")
            form = ProductForm()
        else:
            # print("form is valid")
            if 'product_picture' in request.FILES:
                new_product.image = form.cleaned_data['image']
                # new_product.image = form.cleaned_data['product_image']
                # new_product.content_type = form.cleaned_data['product_picture'].content_type
            # form.save()
            context['message'] = 'Product #{0} saved.'.format(new_product.id)

        new_product.save()

    context['categories'] = Category.objects.all()
    context['products'] = Product.objects.filter(category=request.POST['current_category'])
    context['errors'] = errors

    return render(request, 'groupbuying/shop.html', context)
    # return redirect(reverse('shop', kwargs=context))

@login_required
def update_profile(request):
    context = {}
    errors = []  # A list to record messages for any errors we encounter.
    form = None

    if 'name' not in request.POST or not request.POST['name'] or \
        'price' not in request.POST or not request.POST['price']:
        errors.append('You must have at least "name and price" for the product')
    else:
        new_product = Product(name=str(request.POST['name']),
                              description=str(request.POST['description']),
                              price=float(request.POST['price']),
                              sellerId=str(request.user.id),
                              isAvailable=True,
                              saleVolume=0,
                              vendor=request.user)

        form = ProductForm(request.POST, request.FILES, instance=new_product)
        # form = ImageUploadForm(request.POST, request.FILES)

        if not form.is_valid():
            print("form is NOT valid")
            form = ProductForm()
        else:
            print("form is valid")
            if 'product_picture' in request.FILES:
                new_product.image = form.cleaned_data['image']
                # new_product.image = form.cleaned_data['product_image']
                # new_product.content_type = form.cleaned_data['product_picture'].content_type
            # form.save()
            context['message'] = 'Product #{0} saved.'.format(new_product.id)

        new_product.save()

    products = Product.objects.all()
    context = {'products': products, 'form': form, 'errors': errors}
    print(products)

    return render(request, 'groupbuying/shop.html', context)

@login_required
def get_product_photo(request, id):
    product = get_object_or_404(Product, id=str(id))
    if not product.picture:
        raise Http404

    return HttpResponse(product.picture, content_type=product.content_type)


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
    restaurant[
        'image'] = "https://upload.wikimedia.org/wikipedia/en/thumb/d/d3/Starbucks_Corporation_Logo_2011.svg/1200px-Starbucks_Corporation_Logo_2011.svg.png"

    return restaurant

def get_all_tags():
    all_tag = []

    for obj in VendorInfo.objects.all():
        all_tag = all_tag + category_proc(obj)

    all_tag = list(set(all_tag))
    all_tag = sorted(all_tag)

    return all_tag

def fill_restaurant_context_info(search_result, search_text):
    context = {}
    context['pages'] = range(1, 10)
    context['current_page'] = 1
    context['restaurants'] = []
    context['categories'] = []
    context['query_rules'] = []
    context['last_search_text'] = search_text
    context['rating'] = []
    context['categories'] = get_all_tags()

    for obj in search_result:
        restaurant = fill_restaurant_info(obj)
        context['restaurants'].append(restaurant)
        context['rating'].append(restaurant['rating'])

    if search_text != '':
        context['query_rules'].append(search_text) 
    

    return context

def fill_context_filter_query_rules(context, fitler_query):
    if fitler_query.rating != '':
        context['query_rules'].append(fitler_query.rating) 

    for tag in fitler_query.tag:
        context['query_rules'].append(tag) 
    
    return context

def filtering(request):
    context = {}
    search_text = ''
    fitler_query = lambda:0
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
     
    context = fill_restaurant_context_info(result, search_text)
    context = fill_context_filter_query_rules(context, fitler_query)


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

    for i in range(0,5):
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
    if ('last_search_text' not in request.POST
            or not request.POST['last_search_text']):
        return render(request, 'groupbuying/search.html', context)

    if ('sort_by_name' in request.POST):
        context = sort_by_name(request)

    if ('sort_by_rating' in request.POST):
        context = sort_by_rating(request)

    if ('sort_by_price' in request.POST):
        context = sort_by_price(request)

    return render(request, 'groupbuying/search.html', context)


def sort_by_name(request):
    context = {}
    if ('last_search_text' not in request.POST
            or not request.POST['last_search_text']):
        return render(request, 'groupbuying/search.html', context)

    search_result = search_text_proc(request.POST['last_search_text'])
    #ordered = sorted(search_result, key = lambda w: w.name.lower())
    context = fill_restaurant_context_info(search_result,
                                           request.POST['last_search_text'])
    context['restaurants'] = sorted(context['restaurants'],
                                    key=lambda i: i['name'].lower())

    return context


def sort_by_rating(request):
    context = {}
    if ('last_search_text' not in request.POST
            or not request.POST['last_search_text']):
        return render(request, 'groupbuying/search.html', context)

    search_result = search_text_proc(request.POST['last_search_text'])
    context = fill_restaurant_context_info(search_result,
                                           request.POST['last_search_text'])
    context['restaurants'] = sorted(context['restaurants'],
                                    key=lambda i: i['rating'],
                                    reverse=True)

    return context


def sort_by_price(request):
    context = {}
    if ('last_search_text' not in request.POST
            or not request.POST['last_search_text']):
        return render(request, 'groupbuying/search.html', context)
    # TBD
    search_result = search_text_proc(request.POST['last_search_text'])
    ordered = sorted(search_result, key=lambda w: w.name.lower())
    context = fill_restaurant_context_info(ordered,
                                           request.POST['last_search_text'])

    return context


def search_page(request):
    context = {}
    errors = []

    if request.method == 'GET':
        return render(request, 'groupbuying/search.html', context)

    if ('search_text' not in request.POST or not request.POST['search_text']):
        errors.append('Empty text. Please must enter restaurant info.')
        return render(request, 'groupbuying/search.html', context)

    search_result = search_text_proc(request.POST['search_text'])
    context = fill_restaurant_context_info(search_result,
                                           request.POST['search_text'])

    
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

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    # new_item = UserItem(user_id=new_user.id,
    #                     user_name=form.cleaned_data['username'],
    #                     email=form.cleaned_data['email'],
    #                     first_name=form.cleaned_data['first_name'],
    #                     last_name=form.cleaned_data['last_name'],
    #                     cell_phone=form.cleaned_data['cell_phone'],
    #                     address=form.cleaned_data['address'])
    # new_item.save()

    login(request, new_user)

    return redirect(reverse('home'))
