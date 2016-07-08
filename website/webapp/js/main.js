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
        var tooltip = $("#example-tweet");
        var svg = null;
        var overlay = new google.maps.OverlayView();
        var path = null;
        var overlayProjection = null;

        var clusterDiv = $('.cluster-wrap');

        var selectedCountry = null;
        var selectedClusterType = 'nmf';
        var selectedDate = "20150101";
        var selectedColor = null;
        var clusters = null;

        // geoGson object for Tweets coming from database
        var locationGeoJson =  {type: 'FeatureCollection', features: [] };
        // list for all countries, for which data is available at selected date, coming from database
        var countriesAvailable = [];


        // colors for different clusters
        var colors = ['#8e44ad', '#F62459', '#e67e22', '#E01931', '#2980b9', '#64DDBB', '#FF6861', '#10806E', '#981066', '#002E5A', '#71BA51', '#5659C9', '#F9690E', '#00B5B5', '#B3005A', '#7CA39C', '#918E45', '#E66A39', '#27AE60', '#D33257'];

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
            styles: [{"featureType":"water","elementType":"geometry","stylers":[{"color":"#b9dce6"},{"lightness":17}]},{"featureType":"landscape","elementType":"geometry","stylers":[{"color":"#f5f5f5"},{"lightness":20}]},{"featureType":"road.highway","elementType":"geometry.fill","stylers":[{"color":"#ffffff"},{"lightness":17}]},{"featureType":"road.highway","elementType":"geometry.stroke","stylers":[{"color":"#ffffff"},{"lightness":29},{"weight":0.2}]},{"featureType":"road.arterial","elementType":"geometry","stylers":[{"color":"#ffffff"},{"lightness":18}]},{"featureType":"road.local","elementType":"geometry","stylers":[{"color":"#ffffff"},{"lightness":16}]},{"featureType":"poi","elementType":"geometry","stylers":[{"color":"#f5f5f5"},{"lightness":21}]},{"featureType":"poi.park","elementType":"geometry","stylers":[{"color":"#dedede"},{"lightness":21}]},{"elementType":"labels.text.stroke","stylers":[{"visibility":"on"},{"color":"#ffffff"},{"lightness":16}]},{"elementType":"labels.text.fill","stylers":[{"saturation":36},{"color":"#333333"},{"lightness":40}]},{"elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"geometry","stylers":[{"color":"#f2f2f2"},{"lightness":19}]},{"featureType":"administrative","elementType":"geometry.fill","stylers":[{"color":"#fefefe"},{"lightness":20}]},{"featureType":"administrative","elementType":"geometry.stroke","stylers":[{"color":"#fefefe"},{"lightness":17},{"weight":1.2}]}]
        };

        // Create the Google Map using our element and options defined above
        var map = new google.maps.Map(div.node(), mapOptions);

        var infowindow = new google.maps.InfoWindow({
            content: ''
        });

        var icon = {
            path: google.maps.SymbolPath.CIRCLE,
            fillOpacity: 0.8,
            fillColor: selectedColor,
            strokeWeight: 0,
            scale: 5 //pixels
        };


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

            };

            redraw = function() {
                overlayProjection = this.getProjection();

                if(typeof overlayProjection.getWorldWidth === 'function'){
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
            }

            function redrawCountries(path) {
                var isDragging = false;

                //updating countries
                svg.select('#countries')
                    .selectAll('path')
                    //.filter(function(d) { return d.id == 'RUS' })
                    .attr('d', path)
                    .classed('available', function(d) {
                        if(countriesAvailable.indexOf(d.id) > -1){
                            return true;
                        }
                    })
                    .on("click", function (d) {
                        if (!isDragging) {

                            stateSelected(d);
                        }
                    })
                    .on("mousedown", function () {
                        isDragging = false;
                    })
                    .on("mousemove", function() {
                        isDragging = true;
                    })
                    .on("mouseover", function(){
                        d3.select(this).classed("hover", true);
                        map.setOptions({ draggableCursor: 'pointer' });
                    })
                    .on("mouseout", function(){
                        d3.select(this).classed("hover", false);
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
                    .on("click", function (d) {
                        OpenInNewTab("https://twitter.com/statuses/" + d.properties.id)
                    })
                    //on mouseover tooltip containing tweet text is shown
                    .on("mouseover", function (d) {
                        d3.select(this).style("fill", "#2c3e50");
                        if(d.properties.text.length > 5){
                            tooltip.fadeOut(100, function () {
                                // Popup content
                                tooltip.select('p').html(d.properties.text);
                                $("#example-tweet").fadeIn(100);
                            });
                            tooltip.css({
                                "left": d3.event.pageX + 20,
                                "top": d3.event.pageY
                            });
                        }
                    }).
                    on("mouseout", function () {
                        d3.select(this).style("fill", selectedColor);
                        tooltip.fadeOut(50);
                    })
                    .style("fill", selectedColor);
            }

            function OpenInNewTab(url) {
                var win = window.open(url, '_blank');
                win.focus();
            }

            function stateSelected(d) {

                var state_id = d.id;
                var state_name = d.properties.name;

                console.log(state_id);
                svg.select('#countries')
                    .selectAll('path')
                    // clear focus state for all countries
                    .classed('focus', false)
                    // selected country is set to focus
                    .filter(function(d) { return state_id == d.id;  })
                    .classed('focus', true);

                selectedCountry = state_id;
                setCenter(state_name);
                getClusters();
            }


            // create date picker
            var picker = new Pikaday({
                field: document.getElementById('date'),
                minDate: moment("25-05-2015", "DD-MM-YYYY").toDate(),
                maxDate: moment("31-12-2015", "DD-MM-YYYY").toDate(),
                defaultDate: moment("25-05-2015", "DD-MM-YYYY").toDate(),
                setDefaultDate: true,
                firstDay: 1,
                format: 'D-M-YYYY',
                bound: false,
                container: document.getElementById('date-picker'),
                disableDayFn: function(dateTime){
                    if(new Date(2015, 11, 1) <= dateTime && new Date(2015, 11, 24) > dateTime)
                        return true

                    if(new Date(2015, 4, 31) < dateTime && new Date(2015, 10, 1) > dateTime) {
                            return true
                    }

                },
                onSelect: function () {
                    date = moment(picker.getDate()).format('YYYYMMDD');
                    selectedDate = date;

                    getCountries();
                    getClusters();
                }
            });


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
                    }
                });
            }


            // called after country was selected -- or after new date is selected
            function showTrends(){
                clusterDiv.empty();
                locationGeoJson =  {type: 'FeatureCollection', features: [] };

                $.each( clusters, function( intValue, currentElement ) {
                    var div = ('<div class="cluster" id="cluster-' + currentElement['id'] + '"><div class="terms"></div></div>');
                    clusterDiv.append(div);
                    var terms = currentElement['terms'].split(" ");
                    newWordCloud(terms, currentElement['id'], intValue);
                });
            }

            // creates tag cloud of clusters
            function newWordCloud(words, clusterID, intValue) {
                d3.select('#cluster-' + clusterID)
                    .attr('data-id', clusterID)
                    .attr('style', 'background: ' + colors[intValue] + ';')
                    .select('.terms')
                    .selectAll("span")
                    .data(words)
                    .enter().append("span")
                    .attr("style", function() {
                        size = 12 + Math.random() * 6;
                        opacity = 0.8 + Math.random() * 0.2;
                        return 'font-size: '+ size + 'px; opacity: '+ opacity + '; color: '+ colors[intValue];
                    })
                    .text(function(d) { return d; });

                $('#cluster-' + clusterID).click(function() {
                    selectedColor = colors[intValue];
                    showLocations($(this).attr('data-id'));
                });
            }


            function showLocations(clusterID) {

                svg.select('#countries')
                    .selectAll('path');
                getLocations(clusterID);

                zoom(4);

            }


            // ******* Ajax requests ********

            function getClusters() {
                clusterDiv.empty();
                locationGeoJson =  {type: 'FeatureCollection', features: [] };
                $("#example-tweet").hide();

                clusters = null;
                $('.topics').empty();
                overlay.draw();

                $.ajax({
                    type: "GET",
                    dataType: "json",
                    url: '../website/backend/api/Api.php',
                    data: {
                        action: "getClusters",
                        location: selectedCountry,
                        date: selectedDate,
                        type: getClusteringAlgorithm()
                    },
                    success: function (output) {
                        //console.log(output);
                        clusters = output;
                        showTrends();
                        selectedColor = '#8e44ad';
                        showLocations(clusters[0]['id']);
                    }
                });
            }

            function getLocations(clusterID) {
                locationGeoJson =  {type: 'FeatureCollection', features: [] };
                $("#example-tweet").hide();

                $.ajax({
                    type: "GET",
                    dataType: "json",
                    url: '../website/backend/api/Api.php',
                    data: {
                        action: "getTweets",
                        cluster_id: clusterID,
                        type: selectedClusterType
                    },
                    success: function (output) {
                        locationGeoJson.features = output;
                        overlay.draw();
                        //updateMarkers(output);
                    }
                });
            }

            function getCountries() {
                countriesAvailable = [];

                $.ajax({
                    type: "GET",
                    dataType: "json",
                    url: '../website/backend/api/Api.php',
                    data: {
                        action: "getCountries",
                        date: selectedDate,
                        type: selectedClusterType
                    },
                    success: function (output) {
                        countriesAvailable = output;
                        overlay.draw();
                    }
                });
            }

            getCountries();
            
            function getClusteringAlgorithm() {
                selectedClusterType = $('input[name=optradio]:checked', '#alg-option form').val();
                return selectedClusterType;
            }

            $('input[name=optradio]').on("click", function() {
                selectedClusterType = $('input[name=optradio]:checked', '#alg-option form').val();
                getCountries();
                getClusters();
            });

        }
    });
