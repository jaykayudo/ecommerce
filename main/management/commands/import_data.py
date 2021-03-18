from django.core.management.base import BaseCommand
from collections import Counter
import os.path
import csv
from django.core.files.images import ImageFile
from django.template.defaultfilters import slugify
from main import models

class Command(BaseCommand):
    help = "Import products in BookTime"

    def add_arguments(self,parser):
        parser.add_argument("csvfile",type=open)
        parser.add_argument("image_basedir",type = str)
        

    def handle(self,*args,**options):
        self.stdout.write('Importing Products')
        c = Counter()
        reader = csv.DictReader(options.pop("csvfile"))
        for row in reader:
            product,created = models.Product.objects.get_or_create(name = row['name'],price = row['price'])
            product.description = row['description']
            product.slug = slugify(product.name)
            for import_tag in row['tags'].split('|'):
                producttag,tagcreate = models.ProductTag.objects.get_or_create(name = import_tag)
                product.tags.add(producttag)
                c['producttag'] += 1
                if tagcreate:
                    c['tagcreate'] += 1
                with open(os.path.join(options["image_basedir"],row['image_filename']),'rb') as f:
                    image = models.ProductImage(product=product,
                    image = ImageFile(f,name = row['image_filename'])
                    )
                    image.save()
                    c['image'] += 1
            product.save()
            c['product'] += 1
            if created:
                c['created'] += 1
        self.stdout.write(" Product Processed = %d , created = %d"%(c['product'],c['created']))
        self.stdout.write(" Product Tags Processed = %d , created = %d"%(c['producttag'],c['tagcreate']))
        self.stdout.write(" Product Image Processed = %d"%c['image'])
