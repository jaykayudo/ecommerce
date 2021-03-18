from django.test import TestCase
from django.urls import reverse
from main import forms,models
from django.template.defaultfilters import slugify

# Create your tests here.
class TestPage(TestCase):
    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'home.html')
        self.assertContains(response,'BookTime')
    def test_about_page(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'about.html')
        self.assertContains(response,'BookTime')
    def test_contact_us_page(self):
        response = self.client.get(reverse('contact-us'))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'contact-us.html')
        self.assertContains(response,'Contact Us')
        self.assertIsInstance(
            response.context['form'],
            forms.ContactForm
        )
    def test_list_view(self):
        product,created = models.ProductTag.objects.get_or_create(name ="A Tale")
        product.description = "blah"
        product.slug = slugify(product.name)
        product.save()
        mainproduct = models.Product(name = 'yamy',description='blah',price='10.0')
        mainproduct.tags.set(product)
        mainproduct.save()

        response = self.client.get('products/'+product.slug)
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'main/product-list.html')