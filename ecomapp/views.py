from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic import View,TemplateView,CreateView,FormView
from .models import Product,Category,Cart,CartProduct,Order,Admin,Customer
from .forms import(
		CheckoutForm,CustomerRegistrationForm,
		CustomerLoginForm,AdminLoginForm
	)
from django.urls import reverse_lazy,reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout

# Create your views here.

class HomeView(TemplateView):
	template_name='home.html'

	def get_context_data(self,**kwargs):
		context=super().get_context_data(**kwargs)
		context['myname']='Sagar Tiwari'
		context['product_list']=Product.objects.all().order_by('-id')
		return context

class AllProductsView(TemplateView):
	template_name='allproducts.html'

	def get_context_data(self,**kwargs):
		context=super().get_context_data(**kwargs)
		context['allcategories']=Category.objects.all()
		return context

class ProductDetailView(TemplateView):
	template_name='productdetail.html'

	def get_context_data(self,**kwargs):
		context=super().get_context_data(**kwargs)
		url_slug=self.kwargs['slug']
		product=Product.objects.get(slug=url_slug)
		product.view_count+=1
		product.save()
		context['product']=product
		return context

class AddToCartView(TemplateView):
	template_name='addtocart.html'

	def get_context_data(self,**kwargs):
		context=super().get_context_data(**kwargs)

		product_id=self.kwargs['pro_id']
		product_obj=Product.objects.get(id=product_id)

		cart_id=self.request.session.get('cart_id',None)
		if cart_id:
			cart_obj=Cart.objects.get(id=cart_id)
			this_product_in_cart=cart_obj.cartproduct_set.filter(
				product=product_obj)

			if this_product_in_cart.exists():
				cartproduct=this_product_in_cart.first()
				cartproduct.quantity+=1
				cartproduct.subtotal+=product_obj.selling_price
				cartproduct.save()
				cart_obj.total+=product_obj.selling_price
				cart_obj.save()
			else:
				cartproduct=CartProduct.objects.create(cart=cart_obj,product=product_obj,rate=product_obj.selling_price,quantity=1,subtotal=product_obj.selling_price)
				cart_obj.total+=product_obj.selling_price
				cart_obj.save()
		else:
			cart_obj=Cart.objects.create(total=0)
			self.request.session['cart_id']=cart_obj.id
			cartproduct=CartProduct.objects.create(cart=cart_obj,product=product_obj,rate=product_obj.selling_price,quantity=1,subtotal=product_obj.selling_price)
			cart_obj.total+=product_obj.selling_price
			cart_obj.save()
		return context


class ManageCartView(View):
	def get(self,request,*args,**kwargs):
		cp_id=self.kwargs['cp_id']
		action=request.GET.get('action')
		cp_obj=CartProduct.objects.get(id=cp_id)
		cart_obj=cp_obj.cart

		print(cp_id,action)
		if action=='inc':
			cp_obj.quantity+=1
			cp_obj.subtotal+=cp_obj.rate
			cp_obj.save()
			cart_obj.total+=cp_obj.rate
			cart_obj.save()
		elif action=='dcr':
			cp_obj.quantity-=1
			cp_obj.subtotal-=cp_obj.rate
			cp_obj.save()
			cart_obj.total-=cp_obj.rate
			cart_obj.save()
			if cp_obj.quantity==0:
				cp_obj.delete()
		elif action=='rmv':
			cart_obj.total-=cp_obj.subtotal
			cart_obj.save()
			cp_obj.delete()
		else:
			pass
		return redirect('ecomapp:mycart')

class EmptyCartView(View):
	def get(self,request,*args,**kwargs):
		cart_id=request.session.get('cart_id',None)
		if cart_id:
			cart=Cart.objects.get(id=cart_id)
			cart.cartproduct_set.all().delete()
			cart.total=0
			cart.save()
		return redirect('ecomapp:mycart')


class MyCartView(TemplateView):
	template_name='mycart.html'

	def get_context_data(self,**kwargs):
		context=super().get_context_data(**kwargs)
		cart_id=self.request.session.get('cart_id',None)
		if cart_id:
			cart=Cart.objects.get(id=cart_id)
		else:
			cart=None
		context['cart']=cart
		return context

class CheckoutView(CreateView):
	template_name='checkout.html'
	form_class=CheckoutForm
	success_url=reverse_lazy('ecomapp:home')

	def dispatch(self,request,*args,**kwargs):
		if request.user.is_authenticated and request.user.customer:
			pass
		else:
			return redirect('/customerlogin/?next=/checkout/')
		return super().dispatch(request,*args,**kwargs)

	def get_context_data(self,**kwargs):
		context=super().get_context_data(**kwargs)
		cart_id=self.request.session.get('cart_id',None)
		if cart_id:
			cart_obj=Cart.objects.get(id=cart_id)
		else:
			cart_obj=None
		context['cart']=cart_obj
		return context

	def form_valid(self,form):
		cart_id=self.request.session.get('cart_id',None)
		if cart_id:
			cart_obj=Cart.objects.get(id=cart_id)
			form.instance.cart=cart_obj
			form.instance.subtotal=cart_obj.total
			form.instance.discount=0
			form.instance.total=cart_obj.total
			form.instance.order_status='Order Received'
			del self.request.session['cart_id']
			pm=form.cleaned_data.get('payment_method')
			order=form.save()
			if pm=='Khalti':
				return redirect(reverse('ecomapp:khaltirequest')+ '?o_id=' + str(order.id))
		else:
			return redirect('ecomapp:home')
		return super().form_valid(form)

class KhaltiRequestView(View):
	def get(self,request,*args,**kwargs):
		o_id=request.GET.get('o_id')
		order=Order.objects.get(id=o_id)
		context={
		'order':order
		}
		return render(request,'khaltirequest.html',context)

class CustomerRegistrationView(CreateView):
	template_name='customerregistration.html'
	form_class=CustomerRegistrationForm
	success_url=reverse_lazy('ecomapp:home')

	def form_valid(self,form):
		username=form.cleaned_data.get('username')
		password=form.cleaned_data.get('password')
		email=form.cleaned_data.get('email')
		user=User.objects.create_user(username,email,password)
		form.instance.user=user
		login(self.request,user)
		return super().form_valid(form)

class CustomerLoginView(FormView):
	template_name='customerlogin.html'
	form_class=CustomerLoginForm
	success_url=reverse_lazy('ecomapp:home')

	def form_valid(self,form):
		uname=form.cleaned_data.get('username')
		pword=form.cleaned_data.get('password')
		usr=authenticate(username=uname,password=pword)
		if usr is not None and Customer.objects.filter(user=usr).exists():
			login(self.request,usr)
		else:
			return render(self.request,self.template_name,{'form':self.form_class,'error':'Invalid Credentials'})
		return super().form_valid(form)

	def get_success_url(self):
		if 'next' in self.request.GET:
			next_url=self.request.GET.get('next')
			return next_url
		else:
			return self.success_url


class CustomerLogoutView(View):
	def get(self,request):
		logout(request)
		return redirect('ecomapp:home')

class AboutView(TemplateView):
	template_name='about.html'

class ContactView(TemplateView):
	template_name='contact.html'


class CustomerProfileView(TemplateView):
	template_name='customerprofile.html'

	def dispatch(self,request,*args,**kwargs):
		if request.user.is_authenticated and request.user.customer:
			pass
		else:
			return redirect('/customerlogin/?next=/customerprofile/')
		return super().dispatch(request,*args,**kwargs)


	def get_context_data(self,**kwargs):
		context=super().get_context_data(**kwargs)
		customer=self.request.user.customer
		context['customer']=customer
		orders=Order.objects.filter(cart__customer=customer)
		context['orders']=orders
		return context

# ########### ADMIN PAGES#####################

class AdminLoginView(FormView):
	template_name='adminpages/adminlogin.html'
	form_class=AdminLoginForm
	success_url=reverse_lazy('ecomapp:adminhome')

	def form_valid(self,form):
		uname=form.cleaned_data.get('username')
		pword=form.cleaned_data.get('password')
		usr=authenticate(username=uname,password=pword)
		if usr is not None and Admin.objects.filter(user=usr).exists():
			login(self.request,usr)
		else:
			return render(self.request,self.template_name,{'form':self.form_class,'error':'Invalid Credentials'})
		return super().form_valid(form)
		return super().form_valid(form)

class AdminHomeView(TemplateView):
	template_name='adminpages/adminhome.html'

	def dispatch(self,request,*args,**kwargs):
		if request.user.is_authenticated and Admin.objects.filter(user=request.user).exists():
			pass
		else:
			return redirect('admin-login')
		return super().dispatch(request,*args,**kwargs)

	def get_context_data(self,**kwargs):
		context=super().get_context_data(**kwargs)
		context['pendingorders']=Order.objects.filter(order_status='Order Received')
		return context