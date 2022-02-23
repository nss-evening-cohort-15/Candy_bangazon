from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as auth_token_views
from django.urls import path, include
from bangazon_api import views

router = DefaultRouter(trailing_slash=False)
router.register(r'categories', views.CategoryView, 'category')
router.register(r'orders', views.OrderView, 'order')
router.register(r'payment-types', views.PaymentTypeView, 'payment_type')
router.register(r'products', views.ProductView, 'product')
router.register(r'stores', views.StoreView, 'store')
router.register(r'profile', views.ProfileView, 'profile')

urlpatterns = [
    path('', include(router.urls)),
    path('login', auth_token_views.obtain_auth_token),
    path('register', views.register_user)
]
