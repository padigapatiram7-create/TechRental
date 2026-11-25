"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from users.views import RegisterView, LoginView, LogoutView, ProfileView
from gadgets.views import GadgetViewSet
from cart.views import CartView, AddToCartView, CartItemUpdateView, CartItemDeleteView
from orders.views import CheckoutView, MyOrdersView, OrderDetailView
from lender.views import LenderGadgetsView, LenderOrdersView, LenderOrderActionView, DashboardView

router = DefaultRouter()
router.register('gadgets', GadgetViewSet, basename='gadgets')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/register/', RegisterView.as_view()),
    path('api/users/login/', LoginView.as_view()),
    path('api/users/logout/', LogoutView.as_view()),
    path('api/users/profile/', ProfileView.as_view()),
    path('api/users/refresh/', TokenRefreshView.as_view()),
    path('api/', include(router.urls)),
    path('api/cart/', CartView.as_view()),
    path('api/cart/add/', AddToCartView.as_view()),
    path('api/cart/items/<int:pk>/', CartItemUpdateView.as_view()),
    path('api/cart/items/<int:pk>/delete/', CartItemDeleteView.as_view()),
    path('api/orders/checkout/', CheckoutView.as_view()),
    path('api/orders/', MyOrdersView.as_view()),
    path('api/orders/<int:pk>/', OrderDetailView.as_view()),
    path('api/lender/gadgets/', LenderGadgetsView.as_view()),
    path('api/lender/orders/', LenderOrdersView.as_view()),
    path('api/lender/orders/<int:pk>/advance/', LenderOrderActionView.as_view()),
    path('api/lender/dashboard/', DashboardView.as_view()),
]
