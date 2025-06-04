// JavaScript for test_take.html

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('test-form');
    const questions = document.querySelectorAll('.question-container');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const submitBtn = document.getElementById('submit-btn');
    const progressBar = document.querySelector('.progress');
    const currentQuestionSpan = document.getElementById('current-question');
    const totalQuestionsSpan = document.getElementById('total-questions');
    const timerElement = document.getElementById('timer');
    const testStartedAtInput = document.getElementById('test-started-at');
    
    let currentQuestion = 1;
    const totalQuestions = questions.length;
    let startTime = Date.now();
    let timerInterval;
    
    // Инициализация таймера
    function initTimer() {
        startTime = Date.now();
        // Сохраняем время начала в ISO формате
        testStartedAtInput.value = new Date(startTime).toISOString();
        
        // Запускаем таймер
        timerInterval = setInterval(updateTimer, 1000);
        updateTimer(); // Обновляем сразу
    }
    
    function updateTimer() {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        
        timerElement.textContent = 
            `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
    
    function updateProgress() {
        const progress = ((currentQuestion - 1) / totalQuestions) * 100;
        progressBar.style.width = `${progress}%`;
        currentQuestionSpan.textContent = currentQuestion;
        
        // Показываем/скрываем кнопки
        prevBtn.style.display = currentQuestion > 1 ? 'block' : 'none';
        nextBtn.style.display = currentQuestion < totalQuestions ? 'block' : 'none';
        submitBtn.style.display = currentQuestion === totalQuestions ? 'block' : 'none';
    }
    
    function showQuestion(number) {
        questions.forEach((q, index) => {
            q.style.display = index + 1 === number ? 'block' : 'none';
        });
        currentQuestion = number;
        updateProgress();
    }
    
    prevBtn.addEventListener('click', () => {
        if (currentQuestion > 1) {
            showQuestion(currentQuestion - 1);
        }
    });
    
    nextBtn.addEventListener('click', () => {
        const currentQuestionElement = questions[currentQuestion - 1];
        const selectedAnswer = currentQuestionElement.querySelector('input[type="radio"]:checked');
        
        if (!selectedAnswer) {
            alert('Будь ласка, виберіть відповідь');
            return;
        }
        
        if (currentQuestion < totalQuestions) {
            showQuestion(currentQuestion + 1);
        }
    });
    
    form.addEventListener('submit', function(e) {
        const unansweredQuestions = Array.from(questions).filter(q => {
            const questionId = q.querySelector('input[type="radio"]').name;
            return !form.querySelector(`input[name="${questionId}"]:checked`);
        });
        
        if (unansweredQuestions.length > 0) {
            e.preventDefault();
            alert('Будь ласка, відповідьте на всі питання');
            showQuestion(parseInt(unansweredQuestions[0].dataset.question));
            return;
        }
        
        // Останавливаем таймер при отправке формы
        if (timerInterval) {
            clearInterval(timerInterval);
        }
    });
    
    // Останавливаем таймер при закрытии/перезагрузке страницы
    window.addEventListener('beforeunload', () => {
        if (timerInterval) {
            clearInterval(timerInterval);
        }
    });
    
    // Инициализация
    updateProgress();
    initTimer();
}); 