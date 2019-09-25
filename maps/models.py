import datetime

from django.db import models
from django.forms import ModelForm, HiddenInput


class Point(models.Model):
    name = models.CharField(max_length=30)
    source = models.CharField(max_length=30)
    image = models.ImageField(upload_to='images/')
    date = models.DateField(default=datetime.date.today)
    label = models.IntegerField(null=True, choices=[(0, "No Flood"), (1, "Flood less 1 meter"), (2, "Flood more 1 meter")])
    flood_height = models.DecimalField(max_digits=6, decimal_places=4, default=0)
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


class PointFormComplete(ModelForm):
    class Meta:
        model = Point
        labels = {"label": "Predicted Label", "flood_height": "Predicted Flood Height"}
        exclude = ['image']
        widgets = {
            'source': HiddenInput(),
            'name': HiddenInput(),
            'longitude': HiddenInput(),
            'latitude': HiddenInput(),
            'date': HiddenInput(),
        }
