function init_map(token, latitude_id, longitude_id){

    var marker;
    var clicked = false;

    mapboxgl.accessToken = token;

    var map = new mapboxgl.Map({
      container: 'map',
      style: 'mapbox://styles/mapbox/streets-v11',
      center: [-9.13, 38.71],
      zoom: 3
    });

    map.on('load', () => {
        map.addSource('circleData', {
            type: 'geojson',
            cluster: true,
            clusterMaxZoom: 14,
            clusterRadius: 50,
            data: '/maps/get_geojson'
        });

        map.addLayer({
            id: 'clusters',
            type: 'circle',
            source: 'circleData',
            filter: ["has", "point_count"],
            paint: {
                "circle-color": [
                    "step",
                    ["get", "point_count"],
                    "#51bbd6",
                    100,
                    "#f1f075",
                    750,
                    "#f28cb1"
                ],
                "circle-radius": [
                    "step",
                    ["get", "point_count"],
                    20,
                    100,
                    30,
                    750,
                    40
                ]
            }
        });

        map.addLayer({
            id: "cluster-count",
            type: "symbol",
            source: "circleData",
            filter: ["has", "point_count"],
            layout: {
                "text-field": "{point_count_abbreviated}",
                "text-font": ["DIN Offc Pro Medium", "Arial Unicode MS Bold"],
                "text-size": 12
            }
        });

        map.addLayer({
            id: "unclustered-point",
            type: "circle",
            source: "circleData",
            filter: ["!", ["has", "point_count"]],
            paint: {
                "circle-color": "#11b4da",
                "circle-radius": 4,
                "circle-stroke-width": 1,
                "circle-stroke-color": "#fff"
            }
        });
    });

    map.on('click', 'clusters', function (e) {
        clicked = true;
        let features = map.queryRenderedFeatures(e.point, { layers: ['clusters'] });
        let clusterId = features[0].properties.cluster_id;

        map.getSource('circleData').getClusterExpansionZoom(clusterId, function (err, zoom) {
            if (err)
                return;
            map.easeTo({
                center: features[0].geometry.coordinates,
                zoom: zoom
            });
        });
    });

    map.on('click', 'unclustered-point', function (e) {
        clicked = true;
        let coordinates = e.features[0].geometry.coordinates.slice();
        let description = e.features[0].properties.description;

        new mapboxgl.Popup()
            .setLngLat(coordinates)
            .setHTML(description)
            .addTo(map);
    });

    map.on('mouseenter', 'clusters', function () {
        map.getCanvas().style.cursor = 'pointer';
    });

    map.on('mouseleave', 'clusters', function () {
        map.getCanvas().style.cursor = '';
    });

    map.on('mouseenter', 'unclustered-point', function () {
        map.getCanvas().style.cursor = 'pointer';
    });

     map.on('mouseleave', 'unclustered-point', function () {
        map.getCanvas().style.cursor = '';
    });

    map.on('click', function (e) {
        if (clicked) {
            clicked = false;
            return;
        }
        document.getElementById(latitude_id).value = e.lngLat.lat.toFixed(6);
        document.getElementById(longitude_id).value = e.lngLat.lng.toFixed(6);

        if (marker !== undefined)
            marker.remove();

        marker = new mapboxgl.Marker().setLngLat(e.lngLat).addTo(map);
    });
}


function add_image() {
    let selected =  document.getElementById("add-button").innerHTML !== "Hide";

    if (selected) {
        document.getElementById("col-map").classList.remove('col-12');
        document.getElementById("col-map").classList.add('col-8');
        document.getElementById("form-map").classList.remove('d-none');
        document.getElementById("add-button").innerHTML = "Hide";
    } else {
        document.getElementById("col-map").classList.remove('col-8');
        document.getElementById("col-map").classList.add('col-12');
        document.getElementById("form-map").classList.add('d-none');
        document.getElementById("add-button").innerHTML = "Add New Image";
    }
}

function bodyOnLoad() {
    const imgs = document.querySelectorAll('[data-src]');

    const lazyLoad = target => {
        const io = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.src = entry.target.dataset.src;
                    observer.disconnect();
                }
            });
        });

        io.observe(target);
    };

    imgs.forEach(lazyLoad);
}

function downloadImages() {
    document.getElementById("download-button").disabled = true;
    document.getElementById("download-button").innerHTML = "Please wait...";
    return true;
}