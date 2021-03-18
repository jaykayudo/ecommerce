from django.contrib import admin
from .models import Product, ProductImage, ProductTag, User, Order, OrderLine, Basket, BasketLine,Address
# Register your models here.
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.urls import path
from django.db.models import Avg, Count, Min, Sum
from django.template.response import TemplateResponse
from django.db.models.functions import TruncDay
import datetime
from django import forms
import logging
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template.loader import render_to_string
#for turning html to pdf
#from weasyprint import HTML
import tempfile
from django.contrib.auth.admin import Group, GroupAdmin



logger = logging.getLogger(__name__)


#Note: There are Three Different ways to Register Modelsin this file i.e
#1-  admin.site.register(Model) -> only the Model
#2 - admin.site.register(Model,admin.ModelAdmin Inherited Class) -> model and Created Class inheriting admin.ModelAdmin
#3 - @admin.register(Model) -> which goes above the class  to use which inherits admin.ModelAdmin
# admin.ModelAdmin Inherited class are which is use to style the particular model view in admin

#also note that there are classes which inherits admin.TabularInline
#this classes are created to view models which acts as sub model for a model
# they are not registered but are then passed into the inlines attribute of an admin.Model inheriting class 

#note: raw_id_fields in admin.TabularInline must always be a foriegn key or a many to many field



class InvoiceMixin:
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [path("invoice/<int:order_id>/",self.admin_view(self.invoice_for_order),name="invoice",)]
        return my_urls + urls
    def invoice_for_order(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)
        if request.GET.get("format") == "pdf":
            html_string = render_to_string("invoice.html", {"order": order})
            html = HTML(string=html_string,base_url=request.build_absolute_uri(),)
            result = html.write_pdf()
            response = HttpResponse(content_type="application/pdf")
            
            response["Content-Disposition"] = "inline; filename=invoice.pdf"
            response["Content-Transfer-Encoding"] = "binary"
            with tempfile.NamedTemporaryFile(delete=True) as output:
                output.write(result)
                output.flush()
                output = open(output.name, "rb")
                binary_pdf = output.read()
                response.write(binary_pdf)
            return response
            
        return render(request, "invoice.html", {"order": order})




class ProductAdmin(admin.ModelAdmin):
 
    list_display = ('name', 'slug', 'in_stock', 'price')
    list_filter = ('active', 'in_stock', 'date_updated')
    list_editable = ('in_stock', )
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ('tags',)
    date_hierarchy = 'date_updated'
    actions = ('make_active','make_inactive')

    def make_active(self,request,queryset):
        queryset.update(active = True)
    def make_inactive(self,request,queryset):
        queryset.update(active = False)
    make_active.short_description = 'Make Selected Items Active'
    make_inactive.short_description = 'Make Selected Items Inactive'


    def get_readonly_fields(self,request,obj=None):
        if request.user.is_superuser:
            return self.readonly_fields
        return list(self.readonly_fields) + ['slug','name']
    def get_prepopulated_fields(self,request,obj=None):
        if request.user.is_superuser:
            return self.prepopulated_fields
        else:
            return {}

class DispatchersProductAdmin(admin.ModelAdmin):
    list_display = ('description','price','active')
    autocomplete_fields = ()
    prepopulated_fields = {}
    
    
class ProductTagAdmin(admin.ModelAdmin):
    list_display = ('name','slug','active')
    list_filter = ('active',)
    search_fields = ('name',)
    list_editable = ('active',)
    prepopulated_fields = {"slug":("name",)}

    def get_readonly_fields(self,request,obj=None):
        if request.user.is_superuser:
            return self.readonly_fields
        return list(self.readonly_fields) + ['slug','name']
    def get_prepopulated_fields(self,request,obj=None):
        if request.user.is_superuser:
            return self.prepopulated_fields
        else:
            return {}
    
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_tag','product_name')
    readonly_fields = ('thumbnail_tag',)
    search_fields = ('product_name',)

    def product_name(self,obj):
        return obj.product.name
    def thumbnail_tag(self,obj):
        if obj.thumbnail:
            return format_html('<img src="%s">'%obj.thumbnail.url)
        return '-'
    thumbnail_tag.short_description = "Thumbnail"


# admin.site.register(Product,ProductAdmin)
# admin.site.register(ProductImage,ProductImageAdmin)
# admin.site.register(ProductTag,ProductTagAdmin)

class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None,{"fields":("email","password")}),
        ("Personal info",{"fields":("first_name","last_name")}),
        ("Permission",{"fields":("is_active","is_staff","is_superuser","groups","user_permissions")}),
        ("Important dates",{"fields":("last_login","date_joined")}),
    )
    add_fieldsets = ((None,{"classes":("wide",),"fields":("email","password1","password2")}))

    list_display = ("email","first_name","last_name","is_staff")
    search_fields = ("email","first_name","last_name")
    ordering = ("email",)


# @admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user','name','address_1','zip_code','city','country')
    search_fields = ('user','name')
    readonly_fields = ('user',)

class BasketLineInline(admin.TabularInline):
    model = BasketLine
    raw_id_fields = ('product',)

# @admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ('id','user','status','count')
    list_editable = ('status',)
    search_fields = ('user',)
    list_filter = ('status',)
    list_display_links = ('user',)
    inlines = (BasketLineInline,)
class OrderLineInline(admin.TabularInline):
    model = OrderLine
    raw_id_fields = ('product',)

# @admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id','user','status','billing_name','shipping_name','date_added')
    list_display_links = ('user',)
    list_filter = ('status','shipping_country','date_added')
    list_editable = ('status',)
    inlines = (OrderLineInline,)
    fieldsets = ((None,{'fields':('user','status')}),
            ('Billing Information',{'fields':(
                "billing_name",
                "billing_address1",
                "billing_address2",
                "billing_zip_code",
                "billing_city",    
                "billing_country",
                    )
            }),
            ('Shipping Information',{'fields':(
                "shipping_name",
                "shipping_address1",
                "shipping_address2",
                "shipping_zip_code",
                "shipping_city",    
                "shipping_country",
            )}),
        )

class CentralOfficeOrderLineInline(admin.TabularInline):
    model = OrderLine
    raw_id_fields = ('product',)
class CentralOfficeOrder(admin.ModelAdmin):
    list_display = ('id','user','status')
    readonly_fields = ('user',)
    list_filter = ('status','shipping_country','date_added')
    list_editable = ('status',)
    inlines = (CentralOfficeOrderLineInline,)
    fieldsets = ((None,{'fields':('user','status')}),
            ('Billing Information',{'fields':(
                "billing_name",
                "billing_address1",
                "billing_address2",
                "billing_zip_code",
                "billing_city",    
                "billing_country",
                    )
            }),
            ('Shipping Information',{'fields':(
                "shipping_name",
                "shipping_address1",
                "shipping_address2",
                "shipping_zip_code",
                "shipping_city",    
                "shipping_country",
            )}),
        )
class DispatchOfficeOrder(admin.ModelAdmin):
    list_display = ('id','shipping_name','status','date_added')
    list_filter = ('status','shipping_country','date_added')
    list_editable = ('status',)
    inlines = (CentralOfficeOrderLineInline,)
    fieldsets = (
            ('Shipping Information',{'fields':(
                "shipping_name",
                "shipping_address1",
                "shipping_address2",
                "shipping_zip_code",
                "shipping_city",    
                "shipping_country",
            )}),
        )
    # dispatcher are only allowed to see the orders that is paid and ready to be shipped
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(status= Order.PAID)


# The class below will pass to the Django Admin templates a couple
# of extra values that represent colors of headings
class ColoredAdminSite(admin.sites.AdminSite):
    def each_context(self,request):
        context = super().each_context(request)
        context['site_header_color'] = getattr(self,'site_header_color',None)
        context['module_caption_color'] = getattr(self,'module_caption_color',None)
        return context

# The following will add reporting views to the list of available urls and will list them from the index page

class PeriodSelectionForm(forms.Form):
    CHOICES = ((30,'30 days'),(60,'60 days'),(90,'90 days'))
    picker = forms.TypedChoiceField(choices = CHOICES,required=True, coerce= int, label='Select the Period')

class ReportingColoredAdminSite(ColoredAdminSite):
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('orders_per_day/',self.admin_view(self.orders_per_day)),
            path('most-bought-products/',self.admin_view(self.most_bought_products)),
                ]
        return urls + my_urls
    def most_bought_products(self,request):
        if request.method == 'POST':
            form = PeriodSelectionForm(request.POST)
            if form.is_valid():
                days = form.cleaned_data['picker']
                starting_day = datetime.datetime.now() - datetime.timedelta(days = days)
                data = OrderLine.objects.filter(order__date_added__gt = starting_day).values('product__name').annotate(c = Count('id'))
                logger.info('Most Bought Product is %s'%data.query)
                labels = [x['product__name'] for x in data]
                values = [x['c'] for x in data ]
        else:
            form = PeriodSelectionForm()
            labels = None
            values = None
            
        context = dict(
            self.each_context(request),
            title = "Most Bought Product",
            form = form,
            labels = labels,
            values = values,
            )
        return TemplateResponse(request,'most-bought-products.html',context)


    def orders_per_day(self,request):
        starting_day = datetime.datetime.now() - datetime.timedelta(days = 180)
        orderdata = (Order.objects.filter(date_added__gt = starting_day).annotate(day = TruncDay("date_added"))
        .values('day').annotate(c = Count('id'))
        )
        labels = [
            x["day"].strftime('%Y-%m-%d') for x in orderdata
        ]
        values = [x['c'] for x in orderdata]
        context = dict(
            self.each_context(request),
            title = 'Order Per Day',
            labels = zip(labels,values)
        )
        return TemplateResponse(request,'order_per_day.html',context)
    def index(self, request, extra_context=None):
        reporting_pages = [
            {
                "name": "Orders Per Day",
                "link": "orders_per_day/",
                },
                {
                    'name':'Most Bought Products',
                    "link":'most-bought-products/'
                }
                ]
        if not extra_context:
            extra_context = {}
            extra_context = {"reporting_pages": reporting_pages}
        
        return super().index(request, extra_context)

class OwnersAdminSite(ReportingColoredAdminSite):
    site_header = "BookTime owners administration"
    site_header_color = "black"
    module_caption_color = "grey"
    
    def has_permission(self, request):
        return (request.user.is_active and request.user.is_superuser)


class CentralOfficeAdminSite(ReportingColoredAdminSite):
    site_header = "BookTime central office administration"
    site_header_color = "purple"
    module_caption_color = "pink"
    def has_permission(self, request):
        return (request.user.is_active and request.user.is_employee)

class DispatchersAdminSite(ColoredAdminSite):
    site_header = "BookTime central dispatch administration"
    site_header_color = 'green'
    module_caption_color = 'lightgreen'

    def has_permission(self,request):
        return (request.user.is_active and request.user.is_dispatcher)



main_admin = OwnersAdminSite()
main_admin.register(Product, ProductAdmin)
main_admin.register(ProductTag, ProductTagAdmin)
main_admin.register(ProductImage, ProductImageAdmin)
main_admin.register(User, UserAdmin)
main_admin.register(Group)
main_admin.register(Address, AddressAdmin)
main_admin.register(Basket, BasketAdmin)
main_admin.register(Order, OrderAdmin)
central_office_admin = CentralOfficeAdminSite("central-office-admin")
central_office_admin.register(Product, ProductAdmin)
central_office_admin.register(ProductTag,ProductTagAdmin)
central_office_admin.register(ProductImage, ProductImageAdmin)
central_office_admin.register(Address, AddressAdmin)
central_office_admin.register(Order, CentralOfficeOrder)
dispatchers_admin = DispatchersAdminSite("dispatchers-admin")
dispatchers_admin.register(Product, DispatchersProductAdmin)
dispatchers_admin.register(ProductTag, ProductTagAdmin)
dispatchers_admin.register(Order, DispatchOfficeOrder)



 
