// Scripts for base.html

console.log('Base template loaded');
window.addEventListener('load', function() {
    console.log('All resources loaded');
    // Инициализация всех компонентов Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Add function to toggle admin sidebar menu items
function toggleAdminMenu(element) {
    const menuItem = element.parentElement;
    menuItem.classList.toggle('expanded');
} 