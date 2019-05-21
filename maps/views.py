import zipfile

from io import BytesIO
import os

from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render
from geojson import Point as P
from geojson import Feature, FeatureCollection
from tqdm import tqdm

from SocialFlood.settings import BASE_DIR
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


def images(request):
    media_root = os.path.join(BASE_DIR, 'media')
    img_list = os.listdir(media_root + "\\images")
    ratio = len(img_list) // 4
    if len(img_list) % 4 != 0:
        ratio += 1
    return render(request, 'images.html', {'imgs': img_list, 'ratio': ratio})


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


def download(request):
    print("lol")
    media_root = os.path.join(BASE_DIR, 'media')
    filenames = os.listdir(media_root + "\\images")
    filenames = [media_root + "\\images\\" + f for f in filenames]

    zip_subdir = "dataset"
    zip_filename = "%s.zip" % zip_subdir

    # Open StringIO to grab in-memory ZIP contents
    s = BytesIO()

    # The zip compressor
    zf = zipfile.ZipFile(s, "w")

    for fpath in filenames:
        # Calculate path for file in zip
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)

        # Add file, at correct path
        zf.write(fpath, zip_path)

    # Must close zip for all contents to be written
    zf.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
    # ..and correct content-disposition
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

    return resp
