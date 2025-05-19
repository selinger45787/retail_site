document.addEventListener('DOMContentLoaded', function() {
    const mainImage = document.getElementById('mainImage');
    const thumbnailItems = document.querySelectorAll('.thumbnail-item');

    if (mainImage && thumbnailItems.length > 0) {
        thumbnailItems.forEach(item => {
            item.addEventListener('click', function() {
                // Remove active class from all thumbnails
                thumbnailItems.forEach(thumb => thumb.classList.remove('active'));
                
                // Add active class to clicked thumbnail
                this.classList.add('active');
                
                // Update main image
                const newSrc = this.getAttribute('data-src');
                if (newSrc) {
                    mainImage.src = newSrc;
                }
            });
        });
    }
}); 