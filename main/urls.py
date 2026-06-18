from django.urls import path
from . import views

urlpatterns = [
    # This points the empty path to the 'home' view you created
    path('', views.home, name='home'),
    path('bharatnatyam/',views.bharatnatyam,name='bharatnatyam'),
    path('mohiniyattam/',views.mohiniyattam,name='mohiniyattam'),
    path('kuchipudi/',views.kuchipudi,name='kuchipudi'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin_-home/',views.a_home,name='a_home'),
    path('manage-products/',views.manage_products,name='manage_products'),
    path('jewellery/', views.jewellery, name='jewellery'),
    path('antique-pieces/', views.antique_jewellery, name='antique_jewellery'),
    path('hair-floral/', views.hair_floral, name='hair_floral'),
    path('orders/',views.orders,name='orders'),
]