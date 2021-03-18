from .models import Product, Address, User
import factory
import factory.fuzzy

class UserFactory(factory.django.DjangoModelFactory):
    email = "user@site.com"
    class Meta:
        model = User
        django_get_or_create('email',)
class ProductFactory(factory.django.DjangoModelFactory):
    price = factory.fuzzy.FuzzyDecimal(1.0,1000.0,2)
    class Meta:
        model = Product
class AddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Address

