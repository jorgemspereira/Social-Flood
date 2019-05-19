import datetime

from django.db import models
from django.forms import ModelForm


class Point(models.Model):
    name = models.CharField(max_length=30)
    source = models.CharField(max_length=30)
    image = models.ImageField(upload_to='images/')
    date = models.DateField(default=datetime.date.today)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=0)


"""@receiver(models.signals.post_delete, sender=Point)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)"""


class PointForm(ModelForm):
    class Meta:
        model = Point
        fields = ['name', 'source', 'longitude', 'latitude', 'date', 'image']
