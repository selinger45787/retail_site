// Login Modal
function showLoginModal() {
    const modal = document.getElementById('loginModal');
    if (modal) {
        modal.style.display = 'flex';
        setTimeout(() => {
            modal.classList.add('show');
        }, 10);
    }
}

function closeLoginModal() {
    const modal = document.getElementById('loginModal');
    if (modal) {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.style.display = 'none';
        }, 300);
    }
}

function submitLoginForm() {
    const form = document.getElementById('login-form');
    const formData = new FormData(form);
    const errorDiv = document.getElementById('login-error');
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    
    errorDiv.textContent = '';
    
    // Показываем индикатор загрузки
    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Вхід...';
    
    fetch('/login_modal', {
        method: 'POST',
        body: formData,
        headers: {
            'Accept': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            submitButton.innerHTML = '<i class="fas fa-check"></i> Успішно!';
            submitButton.style.background = 'linear-gradient(145deg, #28a745, #20c997)';
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            errorDiv.textContent = data.message || 'Помилка входу';
            submitButton.disabled = false;
            submitButton.textContent = originalText;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        errorDiv.textContent = 'Помилка з\'єднання з сервером. Спробуйте пізніше.';
        submitButton.disabled = false;
        submitButton.textContent = originalText;
    });
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('loginModal');
    if (event.target == modal) {
        closeLoginModal();
    }
}

// Test Timer
function startTestTimer(duration, display) {
    let timer = duration, minutes, seconds;
    const interval = setInterval(function() {
        minutes = parseInt(timer / 60, 10);
        seconds = parseInt(timer % 60, 10);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        display.textContent = minutes + ":" + seconds;

        if (--timer < 0) {
            clearInterval(interval);
            submitTest();
        }
    }, 1000);
}

// Test Submission
function submitTest() {
    const form = document.getElementById('testForm');
    if (!form) return;

    const formData = new FormData(form);
    const answers = {};

    for (let [key, value] of formData.entries()) {
        const questionId = key.split('_')[1];
        answers[questionId] = value;
    }

    fetch(`/test/submit/${testId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ answers })
    })
    .then(response => response.json())
    .then(data => {
        if (data.score !== undefined) {
            showTestResult(data.score, data.passed);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Произошла ошибка при отправке теста');
    });
}

function showTestResult(score, passed) {
    const resultDiv = document.createElement('div');
    resultDiv.className = 'alert ' + (passed ? 'alert-success' : 'alert-danger');
    resultDiv.innerHTML = `
        <h4>Результат теста</h4>
        <p>Ваш результат: ${score} баллов</p>
        <p>${passed ? 'Поздравляем! Вы сдали тест.' : 'К сожалению, вы не сдали тест.'}</p>
    `;
    
    const form = document.getElementById('testForm');
    form.parentNode.insertBefore(resultDiv, form);
    form.style.display = 'none';
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger';
    errorDiv.textContent = message;
    
    const container = document.querySelector('.container');
    container.insertBefore(errorDiv, container.firstChild);
}

// Material Generation
function generateTest(materialId) {
    fetch(`/test/generate/${materialId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            showSuccess(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Произошла ошибка при генерации теста');
    });
}

function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'alert alert-success';
    successDiv.textContent = message;
    
    const container = document.querySelector('.container');
    container.insertBefore(successDiv, container.firstChild);
    
    setTimeout(() => {
        successDiv.remove();
    }, 3000);
}

// Обработка формы добавления бренда
document.addEventListener('DOMContentLoaded', function() {
    const addBrandForm = document.getElementById('addBrandForm');
    if (addBrandForm) {
        addBrandForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const submitButton = this.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.innerHTML;
            const errorDiv = document.getElementById('brand-error');
            
            // Очищаем предыдущую ошибку
            if (errorDiv) {
                errorDiv.textContent = '';
            }
            
            // Отключаем кнопку и показываем индикатор загрузки
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner"></span> Завантаження...';
            
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content'),
                    'Accept': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.error || 'Помилка при додаванні бренду');
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    window.location.href = data.redirect;
                } else {
                    throw new Error(data.error || 'Помилка при додаванні бренду');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                if (errorDiv) {
                    errorDiv.textContent = error.message;
                } else {
                    alert(error.message || 'Помилка при додаванні бренду');
                }
            })
            .finally(() => {
                // Восстанавливаем кнопку
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
            });
        });
    }
});

// Ініціалізація TinyMCE для текстових полів
document.addEventListener('DOMContentLoaded', function() {
    if (typeof tinymce !== 'undefined') {
        tinymce.init({
            selector: 'textarea#description',
            height: 300,
            menubar: false,
            plugins: [
                'advlist autolink lists link image charmap print preview anchor',
                'searchreplace visualblocks code fullscreen',
                'insertdatetime media table paste code help wordcount'
            ],
            toolbar: 'undo redo | formatselect | bold italic backcolor | \
                     alignleft aligncenter alignright alignjustify | \
                     bullist numlist outdent indent | removeformat | help'
        });
    }
});

// Обработка отправки форм
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form:not(#testForm)');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton && !submitButton.hasAttribute('data-no-spinner')) {
                const originalButtonText = submitButton.innerHTML;
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner"></span> Завантаження...';
                
                // Восстанавливаем кнопку после отправки формы
                setTimeout(() => {
                    submitButton.disabled = false;
                    submitButton.innerHTML = originalButtonText;
                }, 1000);
            }
        });
    });
});

// Анимации для карточек
document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.material-card, .brand-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 8px 12px rgba(0, 0, 0, 0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
        });
    });
});

// Удаляем старые функции для удаления материала
// ... existing code ... 