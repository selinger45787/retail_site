document.addEventListener('DOMContentLoaded', function() {
    const phoneInput = document.querySelector('.phone-input');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            // Удаляем все нецифровые символы
            let value = e.target.value.replace(/\D/g, '');
            
            // Ограничиваем длину до 9 цифр
            value = value.substring(0, 9);
            
            // Просто устанавливаем значение без форматирования
            e.target.value = value;
        });

        // При отправке формы ничего не делаем, так как пробелов уже нет
        phoneInput.form.addEventListener('submit', function(e) {
            // Ничего не делаем, так как пробелов уже нет
        });
    }
}); 