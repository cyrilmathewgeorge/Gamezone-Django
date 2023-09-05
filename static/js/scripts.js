$(document).ready(function() {
    $('#product-img').elevateZoom({
        zoomType: "inner",
        cursor: "crosshair",
        scrollZoom: true,
    });
     // Initialize Cropper.js
    const $image = $('#product-img');
    const cropper = new Cropper($image[0], {
        zoomable: false,
        scalable: false,
        autoCropArea: 1,
        cropBoxMovable: false,
        cropBoxResizable: false,
        dragMode: 'move',
    });

     // Add mousewheel zooming to Cropper.js
    $image.on('mousewheel', function(event) {
        event.preventDefault();
        if (event.originalEvent.deltaY > 0) {
            cropper.zoom(0.1);
        } else {
            cropper.zoom(-0.1);
        }
    });
});