from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from app import views
from app.views import product_detail



urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.home, name='home'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('web/', views.web, name='web'),
    
    # Static pages
    path('about/', views.about, name='about'),
    path('blog/', views.blog, name='blog'),
    path('single/', views.single, name='single'),
    path('wishlist/', views.wishlist, name='wishlist'),

    # Product-related pages
    path('product_detail/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/quick-view/<int:product_id>/', views.quick_view, name='quick_view'),
    path('shop/', views.shop, name='shop'),
    path('shop/<str:category_slug>/', views.shop_view, name='shop_by_category'),

    # Category
    path('category/<str:category_name>/', views.category_detail, name='category_detail'),

    # Cart and checkout
    path('cart/', views.cart, name='cart'),
        path('product/<int:product_id>/', product_detail, name='product_detail'),  # Ensure this line is correct

    path('checkout/', views.checkout, name='checkout'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update_item/', views.updateItem, name='update_item'),

    # Authentication
    path('login/', views.custom_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Search
    path('search/', views.search_products, name='search_products'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),


    # Dashboard and management
    path('d1/', views.d1, name='dashboard'),
    path('add-product/', views.add_product, name='add_product'),
    path('products_list/', views.product_list, name='product_list'),
    path('edit/<int:id>/', views.edit_product, name='edit_product'),
    path('delete/<int:id>/', views.delete_product, name='delete_product'),
    path('upload-excel/', views.upload_excel, name='upload_excel'),
    path('register/', views.register, name='register'),  
    path('product_detail/<int:product_id>/', views.product_detail, name='product_detail'),


]

# Media files (if in debug mode)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
