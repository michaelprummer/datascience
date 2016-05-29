// When the window has finished loading create our google map below
google.maps.event.addDomListener(window, 'load', initMap);
google.maps.event.addDomListener(window, 'resize', redrawOverlay);


var svg;
var map;
var overlay = new google.maps.OverlayView();

var mapElement = document.getElementById('map');

function initMap() {
    // For more options see: https://developers.google.com/maps/documentation/javascript/reference#MapOptions
    var mapOptions = {
        // How zoomed in you want the map to start at (always required)
        zoom: 2,
        minZoom: 2,

        // The latitude and longitude to center the map (always required)
        center: new google.maps.LatLng(40.6700, -73.9400), // New York

        // Source: https://snazzymaps.com/style/151/ultra-light-with-labels
        styles: [{"featureType":"water","elementType":"geometry","stylers":[{"color":"#e9e9e9"},{"lightness":17}]},{"featureType":"landscape","elementType":"geometry","stylers":[{"color":"#f5f5f5"},{"lightness":20}]},{"featureType":"road.highway","elementType":"geometry.fill","stylers":[{"color":"#ffffff"},{"lightness":17}]},{"featureType":"road.highway","elementType":"geometry.stroke","stylers":[{"color":"#ffffff"},{"lightness":29},{"weight":0.2}]},{"featureType":"road.arterial","elementType":"geometry","stylers":[{"color":"#ffffff"},{"lightness":18}]},{"featureType":"road.local","elementType":"geometry","stylers":[{"color":"#ffffff"},{"lightness":16}]},{"featureType":"poi","elementType":"geometry","stylers":[{"color":"#f5f5f5"},{"lightness":21}]},{"featureType":"poi.park","elementType":"geometry","stylers":[{"color":"#dedede"},{"lightness":21}]},{"elementType":"labels.text.stroke","stylers":[{"visibility":"on"},{"color":"#ffffff"},{"lightness":16}]},{"elementType":"labels.text.fill","stylers":[{"saturation":36},{"color":"#333333"},{"lightness":40}]},{"elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"geometry","stylers":[{"color":"#f2f2f2"},{"lightness":19}]},{"featureType":"administrative","elementType":"geometry.fill","stylers":[{"color":"#fefefe"},{"lightness":20}]},{"featureType":"administrative","elementType":"geometry.stroke","stylers":[{"color":"#fefefe"},{"lightness":17},{"weight":1.2}]}]
    };

    // Create the Google Map using our element and options defined above
    map = new google.maps.Map(mapElement, mapOptions);

    overlay.setMap(map);

}


/**
 * onAdd is called when the map's panes are ready and the overlay has been
 * added to the map.
 */
overlay.onAdd = function() {
    var this_ = this;

    svg = d3.select(this_.getPanes().overlayLayer)
        .append("div")
        .attr("id", "d3map")
        .append("svg");

    d3.json("webapp/topo/world-110m.json", function(error, data) {

        svg.append('g')
            .attr('id','countries')
            .selectAll("path")
            .data(topojson.feature(data, data.objects.countries).features)
            .enter()
            .append("path")
            .attr("id", function(d) { return d.id; });
    });

    google.maps.event.addListener(this.map, 'bounds_changed', redrawOverlay);
    google.maps.event.addListener(this.map, 'center_changed', redrawOverlay);
    google.maps.event.addListener(this.map, 'zoom_changed', redrawOverlay);
};

overlay.draw = redrawOverlay;

function redrawOverlay () {
    width = $(mapElement).outerWidth();
    height = $(mapElement).outerHeight();


    svg
        .attr('width', 50000)
        .attr('height', 50000);

    // Moving the overlay back to poitn (0,0) when panning the GoogleMap
    /*overlayLayer = overlay.getPanes().overlayLayer;
     var margin = [];
     var styles = $(overlayLayer).attr('style').split(';');
     margin.left = - parseInt(styles[1].split(':')[1]);
     margin.top = - parseInt(styles[2].split(':')[1]);

     d3.select(overlay.getPanes().overlayLayer)
     .style('margin-left', margin.left + 'px')
     .style('margin-top', margin.top + 'px');*/

    var bounds = map.getBounds(),
        ne = bounds.getNorthEast(),
        sw = bounds.getSouthWest();

    var overlayProjection = d3.geo.mercator()
        .rotate([bounds.getCenter().lng(),0])
        .translate([0,0])
        .center([0,0])
        .scale(1);

    var path = d3.geo.path().projection(overlayProjection);

    var p1 = overlayProjection([ne.lng(),ne.lat()]),
        p2 = overlayProjection([sw.lng(),sw.lat()]);

    svg.select('#countries').attr('transform',
        'scale('+width/(p1[0]-p2[0])+','+height/(p2[1]-p1[1])+')'+
        'translate('+(-p2[0])+','+(-p1[1])+') ');

    svg.selectAll('path').attr('d', path);
}



