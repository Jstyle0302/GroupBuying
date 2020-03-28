import json
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

from groupbuying.forms import LoginForm, RegistrationForm, UserForm
from groupbuying.models import UserItem

# Create your views here.

#@ensure_csrf_cookie
# @login_required
def home_page(request):
    context = {}
    return render(request, 'groupbuying/home.html',context)

def search_page(request):
    context = {}
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
    new_user = User.objects.create_user(username=form.cleaned_data['username'], 
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    new_user.save()

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    new_item = UserItem(user_id=new_user.id,
                        user_name=form.cleaned_data['username'], 
                        email=form.cleaned_data['email'],
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name'],
                        cell_phone=form.cleaned_data['cell_phone'],
                        address=form.cleaned_data['address'])
    new_item.save()
    login(request, new_user)

    return redirect(reverse('home'))