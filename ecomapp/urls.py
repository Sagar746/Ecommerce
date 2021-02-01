from django.urls import path
from .views import(HomeView,AboutView,ContactView,
	AllProductsView,ProductDetailView,AddToCartView,
	MyCartView,ManageCartView,EmptyCartView,CheckoutView,
	CustomerRegistrationView,CustomerLogoutView,CustomerLoginView,
	CustomerProfileView,AdminLoginView,AdminHomeView,KhaltiRequestView
)

app_name='ecomapp'

urlpatterns=[
	path('',HomeView.as_view(),name='home'),
	path('about/',AboutView.as_view(),name='about'),
	path('contact/',ContactView.as_view(),name='contact'),
	path('all_products/',AllProductsView.as_view(),name='allproducts'),
	path('product/<slug:slug>/',ProductDetailView.as_view(),name='productdetail'),
	path('add-to-cart/<int:pro_id>/',AddToCartView.as_view(),name='addtocart'),
	path('my-cart/',MyCartView.as_view(),name='mycart'),
	path('manage-cart/<int:cp_id>/',ManageCartView.as_view(),name='managecart'),
	path('empty-cart/',EmptyCartView.as_view(),name='emptycart'),
	path('checkout/',CheckoutView.as_view(),name='checkout'),

	path('khalti-request/',KhaltiRequestView.as_view(),name='khaltirequest'),

	path('register/',CustomerRegistrationView.as_view(),name='customerregistration'),
	path('customerlogout/',CustomerLogoutView.as_view(),name='customerlogout'),
	path('customerlogin/',CustomerLoginView.as_view(),name='customerlogin'),
	path('profile/',CustomerProfileView.as_view(),name='customerprofile'),

	path('admin-login/',AdminLoginView.as_view(),name='adminlogin'),
	path('admin-home/',AdminHomeView.as_view(),name='adminhome'),



]