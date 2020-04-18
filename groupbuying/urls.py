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
    path('page<int:page>', views.page, name='page'),
    # seller features
    path('shop/<int:shop_id>', views.shop_page, name='shop'),
    path('shop_edit', views.shopEdit_page, name='shop_edit'),
    path('update_vendor_info', views.update_vendor_info, name='update_vendor_info'),
    path('update_vendor_name', views.update_vendor_name, name='update_vendor_name'),
    path('delete_tag/<str:tag_name>', views.delete_tag, name='delete_tag'),
    path('add_category', views.add_category, name='add_category'),
    path('update_category_name', views.update_category_name, name='update_category_name'),
    path('add_product', views.add_product, name='add_product'),
    path('update_product', views.update_product, name='update_product'),
    path('complete_order', views.complete_order, name='complete_order'),
    # customer features
    path('profile-<str:user_id>', views.profile_page, name='profile'),
    path('update_customer_info/<str:user_id>',
         views.update_customer_info, name='update_customer_info'),
    path('other', views.other_page, name='other'),
    path('order/<str:order_id>', views.order_page, name='order'),
    path('orderList', views.orderList_page, name='orderList'),
    path('share/<str:order_id>', views.share_page, name='share'),
    path('show_order/<str:order_id>', views.show_order_page, name='show_order'),
    path('send_email/<str:order_id>', views.send_email_page, name='send_email'),
    path('checkout_to_holder/<str:order_unit_id>',
         views.checkout_to_holder, name='checkout_to_holder'),
    path('checkout_to_shopper/<str:order_id>',
         views.checkout_to_shopper, name='checkout_to_shopper'),
    path('rating_star', views.rating_star, name='rating_star'),
    path('add_to_favorite-<str:shop_id>', views.add_to_favorite, name='add_to_favorite'),
    path('remove_from_favorite-<str:shop_id>', views.remove_from_favorite, name='remove_from_favorite'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
