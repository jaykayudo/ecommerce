from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.edit import FormView, View, CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from . import forms, models
from .models import Address, Order
from django.contrib.auth import authenticate, login, logout
import logging
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import (LoginRequiredMixin,UserPassesTestMixin)
from django import forms as django_forms
from django.db import models as django_models
import django_filters
from django_filters.views import FilterView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import OrderSerializer



# Create your views here.

class ContactView(FormView):
    template_name = 'contact-us.html'
    form_class =  forms.ContactForm
    success_url = '/'


    def form_valid(self,form):
        form.send_mail()
        return super().form_valid(form)

class AllProductListView(ListView):
    template_name = 'main/all_product_list.html'
    paginate_by = 6
    def get_queryset(self):
        products = models.Product.objects.all()
        return products.order_by('date_updated')

class ProductListView(ListView):
    template_name = 'main/product-list.html'
    paginate_by = 4
    def get_queryset(self):
        tag = self.kwargs['tag']
        self.tag = None
        if tag != 'all':
            self.tag = get_object_or_404(models.ProductTag,slug = tag)
        if self.tag:
            products = models.Product.objects.active().filter(tags = self.tag)
        else: 
            products = models.Product.objects.active()
        return products.order_by('name')
    

class ProductDetailView(View):
    template_name = 'main/product-details.html'
    def get(self,request,name):
        product = get_object_or_404(models.Product,slug=name)
        return render(request,'main/product-details.html',{'object':product})


logger = logging.getLogger(__name__)
class SignUpView(FormView):
    template_name = 'main/signup.html'
    form_class = forms.UserCreationForm

    def get_success_url(self):
        redirect_to = self.request.GET.get('next','/')
        return redirect_to
    def form_valid(self,form):
        response = super().form_valid(form)
        form.save()
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password1')
        logger.info('New SignUp for %s through SignUpView'%email)
        user = authenticate(email = email, password = password)
        form.send_mail()
        login(self.request,user)
        messages.info(self.request,'You signed up Successfully')
        return response

class AddressListView(LoginRequiredMixin, ListView):
    model = Address
    template_name = 'main/address-list.html'
    login_url = reverse_lazy('login')
    def get_queryset(self):
        return self.model.objects.filter(user = self.request.user)


class AddressCreateView(LoginRequiredMixin, CreateView):
    model = Address
    template_name = 'main/address-form.html'
    fields = ['name','address_1','address_2','zip_code','country','city']
    success_url = reverse_lazy('address-list')
    
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        return super().form_valid(form)
class AddressUpdateView(LoginRequiredMixin, UpdateView):
    model = Address
    template_name = 'main/address-update.html'
    fields = ['name','address_1','address_2','zip_code','country','city']
    success_url = reverse_lazy('address-list')
    login_url = reverse_lazy('login')

    def get_queryset(self):
        return self.model.objects.filter(user = self.request.user)
class AddressDeleteView(LoginRequiredMixin, DeleteView):
    model = Address
    template_name = 'main/address-delete.html'
    success_url = reverse_lazy('address-list')
    login_url = reverse_lazy('login')

    def get_queryset(self):
        return self.model.objects.filter(user = self.request.user,id=self.kwargs['pk'])





def add_to_basket(request):
    product = get_object_or_404(models.Product, pk=request.GET.get("product_id"))
    basket = request.basket
    if not request.basket:
        if request.user.is_authenticated:
            user = request.user
        else:
            user = None
        
        basket = models.Basket.objects.create(user=user)
        request.session["basket_id"] = basket.id
    basketline, created = models.BasketLine.objects.get_or_create(basket=basket, product=product)
        
    if not created:
        basketline.quantity += 1
        basketline.save()
    
    return HttpResponseRedirect(reverse("product-details", args=(product.slug,)))


def manage_basket(request):
    if not request.basket:
        return render(request,'main/basket.html',{"formset":None})
    if request.method == "POST":
        formset = forms.BasketLineFormSet(request.POST,instance  = request.basket)
        if formset.is_valid():
            formset.save()
    else:
        formset = forms.BasketLineFormSet(instance = request.basket)
    if request.basket.is_empty():
        return render(request,'main/basket.html',{'formset':None})
    return render(request,'main/basket.html',{'formset':formset})


class AddressSelectionView(LoginRequiredMixin, FormView):
    template_name = "main/address-select.html"
    form_class = forms.AddressSelectionForm
    success_url = reverse_lazy('check-done')
    login_url = reverse_lazy('login')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    def form_valid(self,form):
        try:
            del self.request.session['basket_id']
        except KeyError:
            pass
        basket = self.request.basket
        basket.create_order(form.cleaned_data['billing_address'],form.cleaned_data['shipping_address'])
 
        return super().form_valid(form)

class LogUserOut(LoginRequiredMixin, View):
    def get(self,request):
        logout(request=request)
        return redirect('home')


# Order  Dashboard        
class DateInput(django_forms.DateInput):
    input_type = 'date'
class OrderFilter(django_filters.FilterSet):
    class Meta:
        model = models.Order
        fields = {'user__email': ['icontains'],
        'status': ['exact'],
        'date_updated': ['gt', 'lt'],
        'date_added': ['gt', 'lt'],
        }
        filter_overrides = {
            django_models.DateTimeField: {'filter_class': django_filters.DateFilter,
            'extra': lambda f:{'widget': DateInput}}}
class OrderView(UserPassesTestMixin, FilterView):
    filterset_class = OrderFilter
    login_url = reverse_lazy("login")
    def test_func(self):
        return self.request.user.is_staff is True



class UserOrderList(APIView):
    def get(self, request):
        orders = Order.objects.all()
        serializers = OrderSerializer(orders,many=True)
        return Response(serializers.data)
