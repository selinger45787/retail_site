document.addEventListener('DOMContentLoaded', function () {
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const sidebarContainer = document.querySelector('.sidebar-container');
    
    console.log('DOM загружен. Ширина экрана:', window.innerWidth);
    console.log('Кнопка мобильного меню найдена:', !!mobileMenuBtn);
    console.log('Контейнер сайдбара найден:', !!sidebarContainer);

    // Функция для переключения мобильного меню
    function toggleMobileMenu() {
        if (sidebarContainer) {
            sidebarContainer.classList.toggle('mobile-active');
            if (mobileMenuBtn) {
                mobileMenuBtn.classList.toggle('active');
            }
            
            // Предотвращаем прокрутку body когда меню открыто
            if (sidebarContainer.classList.contains('mobile-active')) {
                document.body.style.overflow = 'hidden';
                document.body.classList.add('mobile-menu-open');
            } else {
                document.body.style.overflow = '';
                document.body.classList.remove('mobile-menu-open');
            }
        }
    }

    // Функция для закрытия мобильного меню
    function closeMobileMenu() {
        if (sidebarContainer && window.innerWidth <= 768) {
            sidebarContainer.classList.remove('mobile-active');
            if (mobileMenuBtn) {
                mobileMenuBtn.classList.remove('active');
            }
            document.body.style.overflow = '';
            document.body.classList.remove('mobile-menu-open');
            
            // Закрываем все подменю и сбрасываем состояние элементов
            document.querySelectorAll('.submenu').forEach(submenu => {
                submenu.classList.remove('open');
                resetSubmenuItems(submenu);
            });
            document.querySelectorAll('.menu-item').forEach(item => {
                item.classList.remove('open');
            });
        }
    }

    // Обработчик кнопки мобильного меню
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', toggleMobileMenu);
    }

    // Закрытие меню при клике вне его (только на мобильных)
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768 && sidebarContainer && sidebarContainer.classList.contains('mobile-active')) {
            if (!sidebarContainer.contains(e.target) && !mobileMenuBtn.contains(e.target)) {
                closeMobileMenu();
            }
        }
    });

    // Закрытие меню при изменении размера окна
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768 && sidebarContainer) {
            sidebarContainer.classList.remove('mobile-active');
            if (mobileMenuBtn) {
                mobileMenuBtn.classList.remove('active');
            }
            document.body.style.overflow = '';
            document.body.classList.remove('mobile-menu-open');
            
            // Закрываем все подменю при изменении размера
            document.querySelectorAll('.submenu').forEach(submenu => {
                submenu.classList.remove('open');
                resetSubmenuItems(submenu);
            });
            document.querySelectorAll('.menu-item').forEach(item => {
                item.classList.remove('open');
            });
        }
    });

    const menuItems = document.querySelectorAll('.menu-item');

    menuItems.forEach(item => {
        const title = item.querySelector('.menu-title');
        const submenu = item.querySelector('.submenu');

        if (!title || !submenu) return;

        // Сброс состояния
        resetSubmenuItems(submenu);

        title.addEventListener('click', function (e) {
            console.log('Клик по заголовку, ширина экрана:', window.innerWidth);
            
            if (window.innerWidth <= 768) {
                e.preventDefault();
                e.stopPropagation();
                
                console.log('Обрабатываем клик для мобильного устройства');

                // ВАЖНО: сохраняем состояние ДО изменений
                const isOpen = submenu.classList.contains('open');
                const itemHasOpen = item.classList.contains('open');
                
                console.log('Текущее состояние подменю (открыто):', isOpen);
                console.log('Текущее состояние menu-item (открыто):', itemHasOpen);
                console.log('Классы submenu:', submenu.className);
                console.log('Классы item:', item.className);

                // Закрываем все подменю
                document.querySelectorAll('.submenu').forEach(s => {
                    s.classList.remove('open');
                    resetSubmenuItems(s);
                });

                document.querySelectorAll('.menu-item').forEach(m => {
                    m.classList.remove('open');
                });

                // Используем состояние menu-item как основное
                if (!itemHasOpen) {
                    console.log('Открываем подменю для:', item);
                    item.classList.add('open');
                    submenu.classList.add('open');
                    
                    // Проверяем что классы добавились
                    console.log('После добавления - submenu.open:', submenu.classList.contains('open'));
                    console.log('После добавления - item.open:', item.classList.contains('open'));
                    
                    setTimeout(() => animateSubmenuItems(submenu), 10);
                } else {
                    console.log('Закрываем подменю для:', item);
                }
            } else {
                console.log('Десктопный режим, клик проигнорирован');
            }
        });

        // Для десктопа - анимация при наведении
        item.addEventListener('mouseenter', () => {
            if (window.innerWidth > 768) {
                animateSubmenuItems(submenu);
            }
        });

        item.addEventListener('mouseleave', () => {
            if (window.innerWidth > 768) {
                resetSubmenuItems(submenu);
            }
        });
    });

    // Добавляем обработчики для элементов подменю на мобильных устройствах
    const submenuItems = document.querySelectorAll('.submenu-item');
    submenuItems.forEach(item => {
        item.addEventListener('click', (e) => {
            // Если это ссылка, позволяем переходу произойти и закрываем сайдбар
            if (item.getAttribute('href') && item.getAttribute('href') !== '#') {
                setTimeout(() => {
                    closeMobileMenu();
                }, 100);
            }
        });
    });

    // Свайп-жесты для мобильных устройств
    let touchStartX = 0;
    let touchStartY = 0;
    let touchEndX = 0;
    let touchEndY = 0;

    document.addEventListener('touchstart', function(e) {
        touchStartX = e.changedTouches[0].screenX;
        touchStartY = e.changedTouches[0].screenY;
    }, false);

    document.addEventListener('touchend', function(e) {
        touchEndX = e.changedTouches[0].screenX;
        touchEndY = e.changedTouches[0].screenY;
        handleSwipe();
    }, false);

    function handleSwipe() {
        if (window.innerWidth <= 768) {
            const deltaX = touchEndX - touchStartX;
            const deltaY = touchEndY - touchStartY;
            
            // Проверяем, что это горизонтальный свайп
            if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
                if (deltaX < -100 && sidebarContainer.classList.contains('mobile-active')) {
                    // Свайп влево - закрываем меню
                    closeMobileMenu();
                } else if (deltaX > 100 && !sidebarContainer.classList.contains('mobile-active')) {
                    // Свайп вправо - открываем меню (только если начинаем с левого края)
                    if (touchStartX < 50) {
                        toggleMobileMenu();
                    }
                }
            }
        }
    }

    function animateSubmenuItems(submenu) {
        const items = submenu.querySelectorAll('.submenu-item');
        items.forEach((item, index) => {
            setTimeout(() => {
                item.style.transform = 'translateX(0)';
                item.style.opacity = '1';
            }, index * 25);
        });
    }

    function resetSubmenuItems(submenu) {
        const items = submenu.querySelectorAll('.submenu-item');
        items.forEach(item => {
            item.style.transform = 'translateX(-10px)';
            item.style.opacity = '0';
        });
    }
});
