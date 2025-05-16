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
});