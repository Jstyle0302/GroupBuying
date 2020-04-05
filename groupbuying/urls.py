from django.urls import path
from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
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
    path('add_category', views.add_category, name='add_category'),
    path('add_product', views.add_product, name='add_product'),
    path('get_product_photo/<int:product_id>', views.get_product_photo, name='get_product_photo'),
    path('profile', views.profile_page, name='profile'),
    path('other', views.other_page, name='other'),
    path('order', views.order_page, name='order')
    # path('follower', views.follower_stream, name='follower'),
    # path('follow_user/<int:follower_id>', views.follow_user, name='follow_user'),
    # path('unfollow_user/<int:follower_id>', views.unfollow_user, name='unfollow_user'),

    # path('refresh-global', views.refresh_global, name='refresh-global'),
    # path('refresh-follower', views.refresh_follower, name='refresh-follower'),

    # path('new_post', views.new_post, name='new_post'),
    # path('delete_post/<int:post_id>', views.delete_post, name='delete_post'),
    # path('add-comment/<int:post_id>', views.add_comment, name='add_comment'),
    # path('delete_comment/<int:comment_id>', views.delete_comment, name='delete_comment'),

    # path('upload_photo', views.upload_photo, name='upload_photo'),
    # path('delete-item/<int:id>', views.delete_item, name='delete'),
    # path('photo/<int:id>', views.get_photo, name='photo'),

    # path('user_profile_create', views.user_profile_create, name='user_profile_create'),
    # path('user_profile_edit', views.user_profile_edit, name='user_profile_edit'),
    # path('user_profile_view', views.user_profile_view, name='user_profile_view'),
    # path('other_profile_view/<int:user_id>', views.other_profile_view, name='other_profile_view'),

    # path('search', views.search_action, name='search'),
    # path('create', views.create_action, name='create'),

    # path('delete/<int:id>', views.delete_action, name='delete'),
    # path('edit/<int:id>', views.edit_action, name='edit'),
]
