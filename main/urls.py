from rest_framework import routers
from django.urls import path, re_path
from django.conf.urls import include, url
from django.views.generic import TemplateView
from . import views, forms
from django.contrib.auth import views as auth_view
from rest_framework.urlpatterns import format_suffix_patterns
from . import admin

from . import endpoint


router = routers.DefaultRouter()
router.register(r'orderlines', endpoint.PaidOrderLineViewSet)
router.register(r'orders', endpoint.PaidOrderViewSet)



url_name = ""

urlpatterns = [
    #url(r'^api/order$',include('router.urls')),
    path('', TemplateView.as_view(template_name = "home.html"),name ="home"),
    path('about/', TemplateView.as_view(template_name = "about.html"),name = "about"),
    path('contact-us/',views.ContactView.as_view(),name = "contact-us"),
    path('products/',views.AllProductListView.as_view(),name = 'all-product'),
    path('products/<slug:tag>/',views.ProductListView.as_view(),name='product-list'),
    path('products/details/<slug:name>/',views.ProductDetailView.as_view(),name='product-details'),
    path('signup/',views.SignUpView.as_view(),name = 'signup'),
    path('login/',auth_view.LoginView.as_view(template_name = 'main/login.html',form_class = forms.AuthenticateForm,success_url='/'),name = 'login'),
    path('address/',views.AddressListView.as_view(),name='address-list'),
    path('address/create',views.AddressCreateView.as_view(),name='address-create'),
    path('address/<int:pk>',views.AddressUpdateView.as_view(),name='address-update'),
    path('address/<int:pk>/delete',views.AddressListView.as_view(),name='address-delete'),
    path('add-to-cart/',views.add_to_basket,name='add-to-cart'),
    path('cart/',views.manage_basket,name='cart'),
    path('address-select/',views.AddressSelectionView.as_view(),name='address-select'),
    path('check-done/',TemplateView.as_view(template_name = 'main/check-done.html'),name='check-done'),
    path('logout/',views.LogUserOut.as_view(),name='logout'),
    path("order-dashboard/",views.OrderView.as_view(),name="order_dashboard"),
    # new admin urls
    path("admin/", admin.main_admin.urls),
    path("office-admin/", admin.central_office_admin.urls),
    path("dispatch-admin/", admin.dispatchers_admin.urls),


]
urlpatterns = format_suffix_patterns(urlpatterns)