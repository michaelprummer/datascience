requirejs.config({
    //By default load any module IDs from js/lib
    baseUrl: 'webapp/js/lib'
});


// Start the main app logic.
requirejs(["d3","topojson", "queue", "moment", "pikaday", "d3.layout.cloud"],
    function(d3, topojson, queue, moment, Pikaday, layoutCloud ){

        var width = $('.main').width(),
            height = $('.main').height();

        var div = d3.select('#map');
        var svg;
        var overlay = new google.maps.OverlayView();
        var path;
        var overlayProjection;


        var selectedCountry;
        var selectedTopic;
        var locationGeoJson =  {type: 'FeatureCollection', features: [] };

        var yellow = '#e9d460';
        var red = '#F62459';
        var blue = '#1F3A93';

        // create date picker
        var picker = new Pikaday({
            field: document.getElementById('date'),
            minDate: moment("01-01-2015", "DD-MM-YYYY").toDate(),
            maxDate: moment("31-12-2015", "DD-MM-YYYY").toDate(),
            defaultDate: moment("01-01-2015", "DD-MM-YYYY").toDate(),
            setDefaultDate: true,
            firstDay: 1,
            format: 'D-M-YYYY',
            bound: false,
            container: document.getElementById('date-picker')
        });

        geocoder = new google.maps.Geocoder();

        // For more options see: https://developers.google.com/maps/documentation/javascript/reference#MapOptions
        var mapOptions = {
            // How zoomed in you want the map to start at (always required)
            zoom: 2,
            minZoom: 2,

            // The latitude and longitude to center the map (always required)
            center: new google.maps.LatLng(48.161696, 11.524662),

            draggableCursor: 'initial',

            // Source: https://snazzymaps.com/style/151/ultra-light-with-labels
            styles: [{"featureType":"water","elementType":"geometry","stylers":[{"color":"#e9e9e9"},{"lightness":17}]},{"featureType":"landscape","elementType":"geometry","stylers":[{"color":"#f5f5f5"},{"lightness":20}]},{"featureType":"road.highway","elementType":"geometry.fill","stylers":[{"color":"#ffffff"},{"lightness":17}]},{"featureType":"road.highway","elementType":"geometry.stroke","stylers":[{"color":"#ffffff"},{"lightness":29},{"weight":0.2}]},{"featureType":"road.arterial","elementType":"geometry","stylers":[{"color":"#ffffff"},{"lightness":18}]},{"featureType":"road.local","elementType":"geometry","stylers":[{"color":"#ffffff"},{"lightness":16}]},{"featureType":"poi","elementType":"geometry","stylers":[{"color":"#f5f5f5"},{"lightness":21}]},{"featureType":"poi.park","elementType":"geometry","stylers":[{"color":"#dedede"},{"lightness":21}]},{"elementType":"labels.text.stroke","stylers":[{"visibility":"on"},{"color":"#ffffff"},{"lightness":16}]},{"elementType":"labels.text.fill","stylers":[{"saturation":36},{"color":"#333333"},{"lightness":40}]},{"elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"geometry","stylers":[{"color":"#f2f2f2"},{"lightness":19}]},{"featureType":"administrative","elementType":"geometry.fill","stylers":[{"color":"#fefefe"},{"lightness":20}]},{"featureType":"administrative","elementType":"geometry.stroke","stylers":[{"color":"#fefefe"},{"lightness":17},{"weight":1.2}]}]
        };

        // Create the Google Map using our element and options defined above
        var map = new google.maps.Map(div.node(), mapOptions);

        // Load the  json data
        queue()
            .defer(d3.json, "webapp/topo/countries.topo.json")
            .await(ready);

        function ready(error, data) {
            overlay.setMap(map);

            var countries = topojson.feature(data, data.objects.countries).features;

            overlay.onAdd = function() {
                // create an SVG for the countries
                svg = d3.select(overlay.getPanes().overlayMouseTarget)
                    .append('div')
                    .attr('id','d3map')
                    .append('svg')
                    .attr('width', 8000)
                    .attr('height', 8000);
                svg.append('g')
                    .attr('id','countries')
                    .selectAll('path')
                    .data(countries)
                    .enter().append('path')
                    .attr('id', function(d) { return d.id; });

                svg.append("g").attr("class", "locations");

                overlay.draw = redraw;
                google.maps.event.addListener(map, 'center_changed', redraw);
                google.maps.event.addListener(map, 'bounds_changed', redraw);
                google.maps.event.addListener(map, 'zoom_changed', redraw);

            };

            redraw = function() {

                var markerOverlay = this;
                overlayProjection = markerOverlay.getProjection();
                var worldwidth = overlayProjection.getWorldWidth();
                var prevX = null;

                // Turn the overlay projection into a d3 projection
                var googleMapProjection = function (coordinates) {
                    var googleCoordinates = new google.maps.LatLng(coordinates[1], coordinates[0]);
                    var pixelCoordinates = overlayProjection.fromLatLngToDivPixel(googleCoordinates);

                    if (prevX != null) {
                        // correction of points lying at the edge of the world
                        var dist = pixelCoordinates.x - prevX;
                        if (Math.abs(dist) > (worldwidth * 0.9)) {
                            if (dist > 0) {
                                pixelCoordinates.x -= worldwidth
                            } else {
                                pixelCoordinates.x += worldwidth
                            }
                        }
                    }
                    prevX = pixelCoordinates.x;
                    return [pixelCoordinates.x + 4000, pixelCoordinates.y + 4000];
                }
                path = d3.geo.path().projection(googleMapProjection);

                redrawCountries(path);

                redrawLocations(path);
            }

            function redrawCountries(path) {

                //updating countries
                svg.select('#countries')
                    .selectAll('path')
                    //.filter(function(d) { return d.id == 'RUS' })
                    .attr('d', path)
                    .on("click", stateSelected)
                    .on("mouseover", function(){
                        d3.select(this).classed("hover", !d3.select(this).classed("hover"));
                        map.setOptions({ draggableCursor: 'pointer' });
                    })
                    .on("mouseout", function(){
                        d3.select(this).classed("hover", !d3.select(this).classed("hover"));
                        map.setOptions({ draggableCursor: 'initial' });
                    });
            }

            function redrawLocations(path) {
                // updating locations (circle diagram)
                svg.select('g.locations')
                    .selectAll("path")
                    .remove();

                svg.select('g.locations')
                    .selectAll("path")
                    .data(locationGeoJson.features)
                    .enter().append("path")
                    .attr("d", path.pointRadius(5))
                    .style("fill", function(d) { return d.properties.fill; })
                    .on("mouseover", function (d) {
                        coordinates = d3.mouse(this);
                        var x = coordinates[0] - 4000;
                        var y = coordinates[1] - 4000;
                        $("#example-tweet").fadeOut(100, function () {
                            // Popup content
                            $("#example-tweet p").html(d.properties.text);
                            $("#example-tweet").fadeIn(100);
                        });
                        $("#example-tweet").css({
                            "right": x,
                            "top": y
                        });
                    }).
                    on("mouseout", function () {
                        $("#example-tweet").fadeOut(50);
                    });
            }


            function stateSelected(d) {
                state_id = d.id;
                state_name = d.properties.name;

                svg.select('#countries')
                    .selectAll('path')
                    .attr('class','')
                    .filter(function(d) { return state_id == d.id;  })
                    .attr('class', 'active');

                // reset locations
                locationGeoJson =  {type: 'FeatureCollection', features: [] };

                selectedCountry = state_name;
                //date = picker.getDate();
                console.log(state_name);
                setCenter(state_name);
                showTrends(state_name, date);
            }

            function dateSelected() {

                resetLocations();

                showTrends(selectedCountry, date);
            }

            function zoom(zoom) {
                map.setZoom(zoom);
            }

            function setCenter(state_name) {
                geocoder.geocode( {'address' : state_name}, function(results, status) {
                    if (status == google.maps.GeocoderStatus.OK) {

                        map.setCenter(results[0].geometry.location);
                        zoom(4);
                    }
                });
            }

            // called after country was selected -- or after new date is selected
            function showTrends(state_name, date){

                //TODO
                //getTrends(state_name, date);

                var trend1 = ["dre", "beat", "billionair", "apple"];
                var trend2 = ["cleveland", "football", "brown", "draft", "dallas"];
                var trend3 = ["mexican", "celebrity", "cinco", "mayo"];

                newWordCloud(trend1, yellow, cluster1);
                newWordCloud(trend2, red, cluster2);
                newWordCloud(trend3, blue, cluster3);

            }

            function newWordCloud(words, color, fn) {
                layoutCloud().size([450, 100])
                    .words(words.map(function(d) {
                        return {text: d, size: 14 + Math.random() * 30, fill: color}
                    }))
                    .fontSize(function(d) { return d.size; })
                    .on("end", fn)
                    .start();
            }

            function draw(words, id) {
                d3.select(id)
                    //.selectAll("g").remove()
                    .append("g")
                    .attr("transform", "translate(225,50)")
                    .selectAll("text")
                    .data(words)
                    .enter().append("text")
                    .style("font-size", function(d) { return d.size + "px"; })
                    .style("font-family", "Helvetica Neue")
                    .style("fill", function(d, i) { return d.fill; })
                    .style("opacity", 0.7)
                    .attr("text-anchor", "middle")
                    .attr("transform", function(d) {
                        return "translate(" + [d.x, d.y] + ")rotate(" + 0 + ")";
                    })
                    .text(function(d) { return d.text; });
            }


            function cluster1(words) {
                draw(words, '.cluster-1');
                $('.cluster-1').click(function() {
                    showLocations(1);
                    redraw();
                });
            }
            function cluster2(words) {
                draw(words, '.cluster-2');
                $('.cluster-2').click(function() {
                    showLocations(2);
                    redraw();
                });
            }
            function cluster3(words) {
                draw(words, '.cluster-3');
                $('.cluster-3').click(function() {
                    showLocations(3);
                    redraw();
                });
            }


            function showLocations(cluster) {

                svg.select('#countries')
                    .selectAll('path')
                    .classed('focus',true);


                switch(cluster) {
                    case 2:
                        color = red;
                        break;
                    case 3:
                        color = blue;
                        break;
                    default:
                        color = yellow;
                }

                //load locations of topic
                locationGeoJson.features = [{
                    type: 'Feature',
                    geometry: {type: 'Point', coordinates: [-87.650, 41.850]},
                    properties: {text: 'A', fill: color}
                }, {
                    type: 'Feature',
                    geometry: {type: 'Point', coordinates: [-149.900, 61.218]},
                    properties: {text: 'B', fill: color}
                }, {
                    type: 'Feature',
                    geometry: {type: 'Point', coordinates: [-99.127, 19.427]},
                    properties: {text: 'C', fill: color}
                }, {
                    type: 'Feature',
                    geometry: {type: 'Point', coordinates: [-0.126, 51.500]},
                    properties: {text: 'D', fill: color}
                }, {
                    type: 'Feature',
                    geometry: {type: 'Point', coordinates: [28.045, -26.201]},
                    properties: {text: 'E', fill: color}
                }, {
                    type: 'Feature',
                    geometry: {type: 'Point', coordinates: [15.322, -4.325]},
                    properties: {text: 'F', fill: color}
                }, {
                    type: 'Feature',
                    geometry: {type: 'Point', coordinates: [151.207, -33.867]},
                    properties: {text: 'G', fill: color}
                }, {
                    type: 'Feature',
                    geometry: {type: 'Point', coordinates: [0, 0]},
                    properties: {text: 'H', fill: color}
                }];

                zoom(4);

            }

            $(window).bind("resize", function() {
                redraw();
            });

        }


    });
