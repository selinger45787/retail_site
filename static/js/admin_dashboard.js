document.addEventListener('DOMContentLoaded', function() {
    const addUserForm = document.getElementById('addUserForm');
    
    if (addUserForm) {
        addUserForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            
            fetch('/admin/add_user', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    return response.json();
                }
            })
            .then(data => {
                if (data && data.error) {
                    showError(data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showError('Произошла ошибка при создании пользователя');
            });
        });
    }
});

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger';
    errorDiv.textContent = message;
    
    const form = document.getElementById('addUserForm');
    form.insertBefore(errorDiv, form.firstChild);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
} 