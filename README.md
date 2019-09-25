# Social Flood

Website that uses [mapbox](https://www.mapbox.com/) to display in a global map, all the geo-referenced images used in my MSc
thesis experiments. Within this website, it is also possible to test the model used with your own examples! 
You can download the weights of the considered model [here](https://drive.google.com/open?id=1rEMXj6tbNQLKAwR7GXh7cjJIRc-vo_rQ).
After having downloaded the file place it under the folder `SocialFlood/static/keras`.

### How to use

The code was developed and tested in Python 3.6.7 with [Django](https://www.djangoproject.com/) 2.2.1. 
To run the server, simply execute:

```console
$ python3 manage.py runserver
```

It may take a while since the model is being loaded into the server. 
When the server is running, to access the website please go to `http://127.0.0.1:8000/maps/`, your page should be similar to the one below.

![screenshot](readme/mainpage.png)
