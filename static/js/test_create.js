// JavaScript for test_create.html

let questionCount = 0;

function showFlashMessage(message, type = 'danger') {
    const flashContainer = document.getElementById('flash-messages');
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    flashContainer.appendChild(alertDiv);
    
    // Автоматически скрываем сообщение через 5 секунд
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function checkDuplicateQuestions() {
    const questions = document.querySelectorAll('[name="questions[]"]');
    const questionValues = Array.from(questions).map(q => q.value.trim().toLowerCase());
    const duplicates = new Set();
    
    // Находим дубликаты
    questionValues.forEach((value, index) => {
        if (value && questionValues.indexOf(value) !== questionValues.lastIndexOf(value)) {
            duplicates.add(value);
        }
    });
    
    // Сбрасываем предыдущие стили
    questions.forEach(q => {
        q.classList.remove('is-invalid');
        q.classList.remove('duplicate-question');
    });
    
    // Подсвечиваем дубликаты
    if (duplicates.size > 0) {
        questions.forEach(q => {
            if (duplicates.has(q.value.trim().toLowerCase())) {
                q.classList.add('is-invalid');
                q.classList.add('duplicate-question');
            }
        });
        return false;
    }
    
    return true;
}

function checkDuplicateAnswers(questionDiv) {
    const answers = [
        questionDiv.querySelector('[name="correct_answers[]"]').value.trim(),
        questionDiv.querySelector('[name="wrong_answers_1[]"]').value.trim(),
        questionDiv.querySelector('[name="wrong_answers_2[]"]').value.trim(),
        questionDiv.querySelector('[name="wrong_answers_3[]"]').value.trim()
    ];
    
    const uniqueAnswers = new Set(answers);
    return uniqueAnswers.size === answers.length;
}

function validateForm() {
    const questions = document.querySelectorAll('.card');
    
    // Проверка минимального количества вопросов
    if (questions.length < 5) {
        showFlashMessage('Тест повинен містити мінімум 5 питань');
        return false;
    }
    
    // Проверка дубликатов вопросов
    if (!checkDuplicateQuestions()) {
        showFlashMessage('Знайдено дублікати питань. Будь ласка, перевірте червоні поля.');
        return false;
    }
    
    // Проверка уникальности ответов для каждого вопроса
    for (const question of questions) {
        if (!checkDuplicateAnswers(question)) {
            showFlashMessage('Всі відповіді на одне питання повинні бути унікальними');
            return false;
        }
    }
    
    return true;
}

function addQuestion() {
    const container = document.getElementById('questions-container');
    const questionCount = container.querySelectorAll('.card').length;
    
    const questionDiv = document.createElement('div');
    questionDiv.className = 'card mb-3 question-card';
    questionDiv.innerHTML = `
        <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="card-title">Питання ${questionCount + 1}</h5>
                <button type="button" class="btn btn-danger btn-sm" onclick="removeQuestion(this)">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
            
            <div class="mb-3">
                <label class="form-label">Питання</label>
                <input type="text" class="form-control" name="questions[]" required>
            </div>
            
            <div class="mb-3">
                <label class="form-label">Правильна відповідь</label>
                <input type="text" class="form-control" name="correct_answers[]" required>
            </div>
            
            <div class="mb-3">
                <label class="form-label">Неправильна відповідь 1</label>
                <input type="text" class="form-control" name="wrong_answers_1[]" required>
            </div>
            
            <div class="mb-3">
                <label class="form-label">Неправильна відповідь 2</label>
                <input type="text" class="form-control" name="wrong_answers_2[]" required>
            </div>
            
            <div class="mb-3">
                <label class="form-label">Неправильна відповідь 3</label>
                <input type="text" class="form-control" name="wrong_answers_3[]" required>
            </div>
        </div>
    `;
    
    container.appendChild(questionDiv);
}

function removeQuestion(button) {
    const questionDiv = button.closest('.card');
    questionDiv.remove();
    updateQuestionNumbers();
}

function updateQuestionNumbers() {
    const questions = document.querySelectorAll('.card');
    questions.forEach((question, index) => {
        question.querySelector('.card-title').textContent = `Питання ${index + 1}`;
    });
}

// Добавляем первый вопрос при загрузке страницы, если нет сохраненных данных
document.addEventListener('DOMContentLoaded', function() {
    // Добавляем первый вопрос при загрузке страницы, если нет сохраненных данных
    if (document.querySelectorAll('.card').length === 0) {
        addQuestion();
    }

    // Добавляем контейнер для flash-сообщений, если его нет
    if (!document.getElementById('flash-messages')) {
        const flashContainer = document.createElement('div');
        flashContainer.id = 'flash-messages';
        flashContainer.className = 'container mt-3';
        document.querySelector('form').insertAdjacentElement('beforebegin', flashContainer);
    }
    
    // Добавляем обработчик отправки формы
    const form = document.getElementById('testForm');
    const submitButton = form.querySelector('button[type="submit"]');
    let isSubmitting = false;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (isSubmitting) {
            return;
        }
        
        if (validateForm()) {
            // Если форма валидна, отправляем её
            isSubmitting = true;
            this.submit();
        }
    });
}); 