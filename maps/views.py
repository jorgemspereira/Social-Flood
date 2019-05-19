from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from geojson import Point as P
from geojson import Feature, FeatureCollection

from maps.models import PointForm, Point


def default_map(request):
    # TODO: move this token to Django settings from an environment variable
    mapbox_access_token = 'pk.eyJ1Ijoiam9yZ2Vtc3BlcmVpcmEiLCJhIjoiY2p2ZmJ4anY1MGxhbTQzcGhzOGplMWZoYiJ9.TtOPvUUKoZs27eJGzWDJKQ'

    if request.method == 'POST':
        point_form = PointForm(request.POST, request.FILES)
        if point_form.is_valid():
            query = Point.objects.create(**point_form.cleaned_data)
            query.save()
            return HttpResponseRedirect('/lol/')
    else:
        point_form = PointForm()

    return render(request, 'default.html', {'mapbox_access_token': mapbox_access_token,
                                            'point_form': point_form})


def get_geojson(request):
    features = []
    for point in Point.objects.all():
        properties = {"description": "<h5  align=\"center\">{}</h5>"
                                     "<img height=\"200\" width=\"200\" src=/media/{}> "
                                     "<p style=\"margin-bottom:0\">"
                                     "<b>Source: </b>{}</p>".format(point.name, point.image, point.source)}
        features.append(Feature(geometry=P([point.longitude, point.latitude]), properties=properties))

    feature_collection = FeatureCollection(features)
    return JsonResponse(feature_collection)
