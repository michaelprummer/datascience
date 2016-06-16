requirejs.config({
    //By default load any module IDs from js/lib
    baseUrl: 'webapp/js/lib'

});


// Start the main app logic.
requirejs(["d3","topojson", "queue", "moment", "pikaday"],
    function(d3, topojson, queue, moment, Pikaday ){

        var width = $('.main').width(),
            height = $('.main').height();

        var div = d3.select('#map');
        var svg;
        var overlay = new google.maps.OverlayView();
        var path;
        var overlayProjection;


        var selectedCountry;
        var selectedTopic;
        var selectedColor;
        var locationGeoJson =  {type: 'FeatureCollection', features: [] };

        var lilac = '#8e44ad';
        var red = '#F62459';
        var orange = '#e67e22';

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
            initTopics();

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

                overlayProjection = this.getProjection();
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
                    .attr("d", path.pointRadius(1 * map.getZoom()))
                    .style("fill", function(d) { return d.properties.fill; })
                    .on("mouseover", function (d) {

                        d3.select(this).style("fill", "#2c3e50");

                        pos = d3.mouse(this);
                        var x = pos[0] - 4000;
                        var y = pos[1] - 4000;
                        $("#example-tweet").fadeOut(100, function () {
                            // Popup content
                            $("#example-tweet p").html(d.properties.text);
                            $("#example-tweet").fadeIn(100);
                        });
                        $("#example-tweet").css({
                            "left": x + 20,
                            "top": y
                        });
                    }).
                    on("mouseout", function () {
                        d3.select(this).style("fill", function(d) { return d.properties.fill; });
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
                if (map.getZoom() == zoom) {
                    overlay.draw();
                } else {
                    map.setZoom(zoom);
                }
            }

            function setCenter(state_name) {
                geocoder.geocode( {'address' : state_name}, function(results, status) {
                    if (status == google.maps.GeocoderStatus.OK) {

                        map.setCenter(results[0].geometry.location);
                        zoom(4);
                    }
                });
            }

            function initTopics() {
                $('.topics').click(function() {
                    if ($(this).hasClass('cluster-1')) { selectedColor = lilac; }
                    if ($(this).hasClass('cluster-2')) { selectedColor = red; }
                    if ($(this).hasClass('cluster-3')) { selectedColor = orange; }

                    showLocations();
                });
            }

            // called after country was selected -- or after new date is selected
            function showTrends(state_name, date){

                //TODO
                //getTrends(state_name, date);

                var trend1 = ["dre", "beat", "billionair", "apple", "dre", "beat", "billionairbeat", "apple"];
                var trend2 = ["cleveland", "football", "brown", "draft", "dallas"];
                var trend3 = ["mexican", "celebrity", "cinco", "mayo"];

                newWordCloud(trend1, ".cluster-1");
                newWordCloud(trend2, ".cluster-2");
                newWordCloud(trend3, ".cluster-3");

            }

            function newWordCloud(words, id) {
                d3.select(id)
                    .selectAll("span").remove();
                d3.select(id)
                    .selectAll("span")
                    .data(words)
                    .enter().append("span")
                    .attr("style", function() {
                        size = 12 + Math.random() * 30;
                        opacity = 0.8 + Math.random() * 0.2;
                        return 'font-size: '+ size + 'px; opacity: '+ opacity;
                    })
                    .text(function(d) { return d; });
            }


            function showLocations() {

                svg.select('#countries')
                    .selectAll('path')
                    .classed('focus',true);

                getLocations();

                zoom(4);


            }

            function getLocations() {
                //load locations of topic
                locationGeoJson.features = [{
                    type: 'Feature',
                    geometry: {type: 'Point', coordinates: [13.4351858, 52.5299092]},
                    properties: {text: 'Mobiles : #4092 ORIGINAL Monster Beats by Dr Dre iBeats In-Ear Headphones for Apple iPhone… ', fill: selectedColor}
                },
                {
                    type: 'Feature',
                    geometry: {type: 'Point', coordinates: [11.581981, 48.135125]},
                    properties: {text: 'Text', fill: selectedColor}
                }];
            }

        }


    });
