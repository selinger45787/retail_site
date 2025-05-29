document.addEventListener('DOMContentLoaded', function () {
    const isMobile = window.innerWidth <= 768;

    // Анимация появления элементов подменю
    function animateSubmenuItems(submenu, show = true) {
        const items = submenu.querySelectorAll('.submenu-item');
        items.forEach((item, index) => {
            setTimeout(() => {
                if (show) {
                    item.style.transform = 'translateX(0)';
                    item.style.opacity = '1';
                } else {
                    item.style.transform = 'translateX(-10px)';
                    item.style.opacity = '0';
                }
            }, index * 50);
        });
    }

    if (isMobile) {
        const menuItems = document.querySelectorAll('.menu-item');

        menuItems.forEach(item => {
            const title = item.querySelector('.menu-title');
            const submenu = item.querySelector('.submenu');

            if (!title || !submenu) return;

            title.addEventListener('click', e => {
                e.preventDefault();

                const isOpen = submenu.classList.contains('open');

                // Закрываем все другие подменю
                document.querySelectorAll('.submenu').forEach(s => {
                    if (s !== submenu) {
                        s.classList.remove('open');
                        animateSubmenuItems(s, false);
                    }
                });
                document.querySelectorAll('.menu-item').forEach(m => {
                    if (m !== item) m.classList.remove('open');
                });

                if (!isOpen) {
                    submenu.classList.add('open');
                    item.classList.add('open');
                    setTimeout(() => animateSubmenuItems(submenu, true), 100);
                } else {
                    animateSubmenuItems(submenu, false);
                    setTimeout(() => {
                        submenu.classList.remove('open');
                        item.classList.remove('open');
                    }, 200);
                }
            });
        });
    } else {
        // Для десктопа - анимация при наведении
        const menuItems = document.querySelectorAll('.menu-item');
        
        menuItems.forEach(item => {
            const submenu = item.querySelector('.submenu');
            
            if (!submenu) return;
            
            item.addEventListener('mouseenter', () => {
                setTimeout(() => animateSubmenuItems(submenu, true), 150);
            });
            
            item.addEventListener('mouseleave', () => {
                animateSubmenuItems(submenu, false);
            });
        });
    }

    // Плавная прокрутка сайдбара
    const sidebar = document.querySelector('.sidebar-container');
    if (sidebar) {
        sidebar.style.scrollBehavior = 'smooth';
    }
});