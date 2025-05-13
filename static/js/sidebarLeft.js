document.addEventListener('DOMContentLoaded', function () {
    const isMobile = window.innerWidth <= 768;

    if (isMobile) {
        const menuItems = document.querySelectorAll('.menu-item');

        menuItems.forEach(item => {
            const title = item.querySelector('.menu-title');
            const submenu = item.querySelector('.submenu');

            if (!title || !submenu) return;

            title.addEventListener('click', e => {
                e.preventDefault();

                const isOpen = submenu.classList.contains('open');

                document.querySelectorAll('.submenu').forEach(s => s.classList.remove('open'));
                document.querySelectorAll('.menu-item').forEach(m => m.classList.remove('open'));

                if (!isOpen) {
                    submenu.classList.add('open');
                    item.classList.add('open');
                }
            });
        });
    }
});