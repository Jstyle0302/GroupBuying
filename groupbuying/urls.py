from django.urls import path
from django.conf import settings
from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('login', views.login_action, name='login'),
    path('logout', views.logout_action, name='logout'),
    path('register', views.register_action, name='register'),
    url(r'oauth/', include('social_django.urls', namespace='social')),
    # search features
    path('search', views.search_page, name='search'),
    path('sorting', views.sorting, name='sorting'),
    path('filtering', views.filtering, name='filtering'),
    path('page/<int:page>', views.page, name='page'),
    # seller features
    path('shop', views.shop_page, name='shop'),
    path('update_vendor_info', views.update_vendor_info, name='update_vendor_info'),
    path('add_category', views.add_category, name='add_category'),
    path('add_product', views.add_product, name='add_product'),
    path('update_product/<int:product_id>', views.update_product, name='update_product'),
    path('get_product_photo/<int:product_id>', views.get_product_photo, name='get_product_photo'),
    # customer features
    path('profile', views.profile_page, name='profile'),
    path('other', views.other_page, name='other'),
    path('order', views.order_page, name='order'),
    path('share', views.share_page, name='share'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)