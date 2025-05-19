document.addEventListener('DOMContentLoaded', function () {
    const deleteBtn = document.getElementById('deleteMaterialBtn');
    const csrfToken = document.getElementById('csrf-token')?.value;

    if (deleteBtn) {
        deleteBtn.addEventListener('click', async function () {
            const confirmed = confirm('Ви впевнені, що хочете видалити цей матеріал?');
            if (!confirmed) return;

            const actionUrl = deleteBtn.getAttribute('data-url');

            try {
                const response = await fetch(actionUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: new URLSearchParams({ csrf_token: csrfToken })
                });

                const result = await response.json();

                if (result.success && result.redirect) {
                    window.location.href = result.redirect;
                } else {
                    alert(result.error || 'Помилка при видаленні матеріалу.');
                }
            } catch (err) {
                console.error('Помилка при fetch:', err);
                alert('Сервер не відповідає. Спробуйте пізніше.');
            }
        });
    }

    // Обработка кликов по миниатюрам
    const thumbnails = document.querySelectorAll('.thumbnail-item');
    const mainImage = document.getElementById('mainImage');

    thumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', function() {
            // Убираем активный класс у всех миниатюр
            thumbnails.forEach(t => t.classList.remove('active'));
            // Добавляем активный класс к выбранной миниатюре
            this.classList.add('active');
            
            // Обновляем главное изображение с анимацией
            const newSrc = this.getAttribute('data-src');
            if (mainImage && newSrc) {
                // Добавляем класс для анимации исчезновения
                mainImage.classList.add('fade-out');
                
                // После завершения анимации исчезновения меняем изображение
                setTimeout(() => {
                    mainImage.src = newSrc;
                    // Добавляем класс для анимации появления
                    mainImage.classList.remove('fade-out');
                    mainImage.classList.add('fade-in');
                    
                    // Убираем класс анимации появления после её завершения
                    setTimeout(() => {
                        mainImage.classList.remove('fade-in');
                    }, 300);
                }, 300);
            }
        });
    });
});