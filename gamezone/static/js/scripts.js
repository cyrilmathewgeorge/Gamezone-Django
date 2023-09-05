<script>
    $(document).ready(function() {
        $(".xzoom, .xzoom-gallery").xzoom({
            zoomWidth: 400,
            tint: "#333",
            Xoffset: 15
        });
    });

    // Vanilla JavaScript for hover zoom (assuming you have an element with class 'product-image')
    const productImage = document.querySelector('.product-image');

    productImage.addEventListener('mouseover', () => {
        productImage.style.transform = 'scale(1.5)'; // Increase the scale for zoom
        productImage.style.transition = 'transform 0.3s'; // Add a smooth transition
    });

    productImage.addEventListener('mouseout', () => {
        productImage.style.transform = 'scale(1)'; // Reset the scale
        productImage.style.transition = 'transform 0.3s'; // Add a smooth transition
    });
</script>
