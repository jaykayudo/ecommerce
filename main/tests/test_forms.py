from django.test import TestCase, override_settings
from django.core import mail
from main import forms, models
from decimal import Decimal
from django.core.files.images import ImageFile
from io import StringIO
from django.core.management import call_command
from django.conf import settings
import tempfile



class TestForm(TestCase):
    def test_valid_contact_us(self):
        form = forms.ContactForm({'name':'Josh Kay','message':'Testing Django Mail'})
        self.assertTrue(form.is_valid())
        with self.assertLogs('main.forms',level='INFO') as cm:
            form.send_mail()
        self.assertEqual(len(mail.outbox),1)
        self.assertEqual(mail.outbox[0].subject,'Site Message')
        self.assertGreaterEqual(len(cm.output),1)
    
    def test_invalid_contact_us(self):
        form = forms.ContactForm({'message':'Hi There'})

        self.assertFalse(form.is_valid())

class TestModel(TestCase):
    def test_manager(self):
        models.Product.objects.create(name= 'The caterdral and bazzarr',price=Decimal("10.00"))
        models.Product.objects.create(name= 'The Tale of Pride',price=Decimal("12.00"))
        models.Product.objects.create(name= 'The Tales of Two Cities',price=Decimal("15.00"),active = False)

        self.assertEqual(len(Product.objects.active()),2)
class TestSignal(TestCase):    
    def test_thumbnails_are_generated_on_save(self):
        product = models.Product(name="The cathedral and the bazaar",price=Decimal("10.00"),)
        product.save()
        with open("main/fixtures/christmas design.jpg", "rb") as f:
            image = models.ProductImage(product=product,image=ImageFile(f, name="christmas design.jpg"),)
        with self.assertLogs("main", level="INFO") as cm:
            image.save()

        self.assertGreaterEqual(len(cm.output),1)
        image.refresh_from_db()
        with open("main/fixtures/christmas design.thumb.jpg","rb") as f:
            expected_content = f.read()
        assert image.thumbnail.read() == expected_content
        image.thumbnail.delete(save = False)
        image.image.delete(save = False)
class TestCommand(TestCase):
    @override_settings(MEDIA_ROOT = tempfile.gettempdir() )
    def test_import_command(self):
        out = StringIO()
        args = ['main/fixtures/productcsvfile.csv','main/fixtures/productimages/']
        expected_out = ('Importing Products\nProduct Processed = 3 , created = 3\n'+
                        'Product Tags Processed = 6 , created = 6\n'+
                        'Product Image Processed = 6'  )
        call_command("import_data",*args,stdout = out)

        self.assertEqual(models.Product.objects.count(),3)
        self.assertEqual(models.ProductTag.objects.count(),6)
        self.assertEqual(models.ProductImage.objects.count(),6)

        #self.assertEqual(out.getvalue(),expected_out)
        with open(args[0],'r') as file:
            self.assertTrue(file.readable(),True)
        
