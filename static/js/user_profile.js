// JS для страницы Личного кабинета пользователя 

// User Profile page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const testRows = document.querySelectorAll('.test-row');
    
    testRows.forEach(row => {
        row.addEventListener('click', function() {
            const materialId = this.dataset.materialId;
            window.location.href = `/material/${materialId}`;
        });
    });
}); 