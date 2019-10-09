import os
import zipfile
from base64 import b64encode, b64decode
from io import BytesIO

import numpy as np
from django.core.files.base import ContentFile
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from geojson import Feature, FeatureCollection
from geojson import Point as P
from keras.preprocessing.image import load_img, img_to_array

from SocialFlood.settings import BASE_DIR, MB_ACCESS_TK, gGraph, gModel
from maps.models import PointForm, Point, PointFormComplete


def pre_process_img(img):
    x = load_img(img, target_size=(224, 224))
    x = img_to_array(x)
    x = np.divide(x, 255)
    return np.expand_dims(x, axis=0)


def default_map(request):
    if request.method == 'POST':
        point_form = PointForm(request.POST, request.FILES)
        point_form_complete = PointFormComplete(request.POST, request.FILES)

        if point_form.is_valid():
            query = Point(**point_form.cleaned_data)
            content = b64encode(query.image.file.read()).decode('ascii')

            with gGraph.as_default():
                predictions = gModel.predict(pre_process_img(query.image), batch_size=1)

            label = np.argmax(predictions[0])
            height = round(predictions[1][0][0], 4)

            point_form_complete = PointFormComplete(initial=
                                                    {'label': Point._meta.get_field('label').choices[label],
                                                     'flood_height': height,
                                                     'source': query.source,
                                                     'name': query.name,
                                                     'longitude': query.longitude,
                                                     'latitude': query.latitude,
                                                     'date': query.date})

            request.session['image'] = content
            request.session['image_path'] = query.image.name
            ext = query.image.name.split(".")[-1]

            return render(request, 'default.html', {'mapbox_access_token': MB_ACCESS_TK,
                                                    'image_src': "data:image/" + ext + ";base64," + content,
                                                    'point_form_complete': point_form_complete})

        if point_form_complete.is_valid():
            query = Point.objects.create(**point_form_complete.cleaned_data)
            query.image.save(request.session['image_path'],
                             ContentFile(b64decode(request.session['image'])))
            query.save()
            return HttpResponseRedirect("default.html")

    return render(request, 'default.html', {'mapbox_access_token': MB_ACCESS_TK, 'point_form': PointForm(),
                                            'point_form_complete': None})


def back_button(request):
    return redirect(reverse('maps'))


def images(request):
    media_root = os.path.join(BASE_DIR, 'media')
    img_list = os.listdir(media_root + "\\images")
    ratio = len(img_list) // 4
    if len(img_list) % 4 != 0:
        ratio += 1
    return render(request, 'images.html', {'imgs': img_list, 'ratio': ratio})


def about(request):
    return render(request, 'about.html')


def get_geojson(request):
    features = []
    media_root = os.path.join(BASE_DIR, 'media')
    for point in Point.objects.all():
        if point.label is None:
            properties = {"description": "<h5  align=\"center\">{}</h5>"
                                         "<img height=\"200\" width=\"200\" src=/media/{}> "
                                         "<p style=\"margin-bottom:0\">"
                                         "<b>Source: </b>{}</p>".format(point.name, point.image, point.source)}
        else:
            properties = {"description": "<h5  align=\"center\">{}</h5>"
                                         "<img height=\"200\" width=\"200\" src=/media/{}> "
                                         "<p style=\"margin-bottom:0\">"
                                         "<b>Source: </b>{}</p>"
                                         "<p style=\"margin-bottom:0\">"
                                         "<b>Class: </b>{}</p>"
                                         "<p style=\"margin-bottom:0\">"
                                         "<b>Height: </b>{} m</p>".format(point.name, point.image, point.source,
                                                                          Point._meta.get_field('label').choices[point.label][1],
                                                                          point.flood_height)}
        features.append(Feature(geometry=P([point.longitude, point.latitude]), properties=properties))

    feature_collection = FeatureCollection(features)
    return JsonResponse(feature_collection)


def download(request):
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
