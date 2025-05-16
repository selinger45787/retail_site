// JavaScript для админской панели
document.addEventListener('DOMContentLoaded', function() {
    console.log('Admin sidebar initialized');
    
    // Добавляем обработчики для выпадающего меню
    const adminMenu = document.querySelector('.admin-menu-wrapper');
    if (adminMenu) {
        adminMenu.addEventListener('mouseenter', function() {
            this.querySelector('.admin-dropdown-menu').style.display = 'block';
        });
        
        adminMenu.addEventListener('mouseleave', function() {
            this.querySelector('.admin-dropdown-menu').style.display = 'none';
        });
    }
}); 