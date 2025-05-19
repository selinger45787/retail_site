document.addEventListener('DOMContentLoaded', function() {
    const testTable = document.querySelector('.test-table');
    if (testTable) {
        const rows = testTable.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            row.addEventListener('click', function() {
                const materialId = this.getAttribute('data-material-id');
                if (materialId) {
                    window.location.href = `/material/${materialId}`;
                }
            });
        });
    }
}); 