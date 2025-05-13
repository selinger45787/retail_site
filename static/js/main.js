// Login Modal
function showLoginModal() {
    const modal = document.getElementById('loginModal');
    if (modal) {
        modal.style.display = 'block';
    }
}

function closeLoginModal() {
    const modal = document.getElementById('loginModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function submitLoginForm() {
    const form = document.getElementById('login-form');
    const formData = new FormData(form);
    
    fetch('/login', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        } else {
            return response.text();
        }
    })
    .then(data => {
        if (data) {
            const errorDiv = document.getElementById('login-error');
            if (errorDiv) {
                errorDiv.textContent = 'Неверный логин или пароль';
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        const errorDiv = document.getElementById('login-error');
        if (errorDiv) {
            errorDiv.textContent = 'Произошла ошибка при входе';
        }
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

// Функции для работы с модальными окнами
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Закрытие модального окна при клике вне его содержимого
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Инициализация TinyMCE для текстовых полей
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
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner"></span> Завантаження...';
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