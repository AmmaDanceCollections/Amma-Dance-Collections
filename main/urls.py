from django.urls import path
from . import views

urlpatterns = [
    # Core & Homepage
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('catalog/filter/', views.catalog_filter, name='catalog_filter'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

    # E-Commerce Flow
    #path('cart/', views.cart_page, name='cart_page'),
    #path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    #path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    #path('checkout/', views.checkout, name='checkout'),
    #path('checkout/success/', views.order_success, name='order_success'),

    # Favorites
    path('favorites/toggle/<int:product_id>/', views.toggle_favorite, name='toggle_favorite'),

    # Product Categories
    path('bharatnatyam/', views.bharatnatyam, name='bharatnatyam'),
    path('mohiniyattam/', views.mohiniyattam, name='mohiniyattam'),
    path('kuchipudi/', views.kuchipudi, name='kuchipudi'),
    path('jewellery/', views.jewellery, name='jewellery'),
    path('antique-pieces/', views.antique_jewellery, name='antique_jewellery'),
    path('hair-floral/', views.hair_floral, name='hair_floral'),

    # Admin Command Center
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin_-home/', views.a_home, name='a_home'),
    path('manage-products/', views.manage_products, name='manage_products'),
    path('orders/', views.orders, name='orders'),
]