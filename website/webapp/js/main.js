requirejs.config({
    //By default load any module IDs from js/lib
    baseUrl: 'webapp/js/lib'
});


// Start the main app logic.
requirejs(["d3","topojson", "queue", "moment", "pikaday", "d3.layout.cloud"],
    function(d3, topojson, queue, moment, Pikaday, layoutCloud ){

        var width = $('.main').width(),
            height = $('.main').height();

        var selectedCountry;
        var selectedTopic;


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


        var div = d3.select('#map');
        var svg;
        var locations;
        var overlay = new google.maps.OverlayView();
        var path;
        var overlayProjection;

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
            var countries = topojson.feature(data, data.objects.countries).features;

            overlay.onAdd = function() {
                // create an SVG over top of it.
                svg = d3.select(overlay.getPanes().overlayMouseTarget)
                    .append('div')
                    .attr('id','d3map')
                    .append('svg')
                    .attr('width', 8000)
                    .attr('height', 8000);

                locations = d3.select(overlay.getPanes().overlayMouseTarget)
                    .append('div')
                    .attr('id','dataLayer')
                    .append('svg')
                    .attr('width', 8000)
                    .attr('height', 8000);

                svg.append('g')
                    .attr('id','countries')
                    .selectAll('path')
                    .data(countries)
                    .enter().append('path')
                    .attr('id', function(d) { return d.id; });

                locations.append('g')
                    .attr('id','locations');


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
                        // Check for a gigantic jump to prevent wrapping around the world
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

                svg.selectAll('path')
                    //.filter(function(d) { return d.id == 'RUS' })
                    .attr('d', path)
                    .on("click", state_clicked)
                    .on("mouseover", function(){
                        d3.select(this).classed("hover", !d3.select(this).classed("hover"));
                        map.setOptions({ draggableCursor: 'pointer' });
                    })
                    .on("mouseout", function(){
                        d3.select(this).classed("hover", !d3.select(this).classed("hover"));
                        map.setOptions({ draggableCursor: 'initial' });
                    });
            }

            function state_clicked(d) {
                state_id = d.id;
                state_name = d.properties.name;

                svg.selectAll('path')
                    .attr('class','')
                    .filter(function(d) { return state_id == d.id;  })
                    .attr('class', 'active');

                selectedCountry = state_name;
                setCenter(state_name);
                getTrends(state_name);

            }

            function topicClicked() {

                svg.selectAll('path')
                    .classed('active',false);

                showDistribution();
                zoom(4);
            }



            function setCenter(state_name) {
                geocoder.geocode( {'address' : state_name}, function(results, status) {
                    if (status == google.maps.GeocoderStatus.OK) {
                        if (map.getZoom() < 4) {
                            map.setCenter(results[0].geometry.location);
                        }
                    }
                });
            }

            function zoom(zoom) {
                map.setZoom(zoom);
            }

            overlay.setMap(map);

            function getTrends(state_name){

                newWordCloud(["dre", "beat", "billionair", "apple"], '#e9d460', cluster1);
                newWordCloud(["cleveland", "football", "brown", "draft", "dallas"], '#F62459', cluster2);
                newWordCloud(["mexican", "celebrity", "cinco", "mayo"], '#1F3A93', cluster3);

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
                    topicClicked();
                });
            }
            function cluster2(words) {
                draw(words, '.cluster-2');
            }
            function cluster3(words) {
                draw(words, '.cluster-3');
            }

            $(window).bind("resize", function() {
                redraw();
            });


            function showDistribution() {
                var topicFound = {"1":[-122.05,37.43], "2":[-120.12,36.98]};

                var circles = d3.select(overlay.getPanes().overlayMouseTarget)
                    .append
            }
        }


    });
