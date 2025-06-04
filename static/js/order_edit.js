// Scripts for order edit page

document.addEventListener('DOMContentLoaded', function() {
    let editor = null;
    
    // Initialize CKEditor
    ClassicEditor
        .create(document.querySelector('#description'), {
            toolbar: [
                'heading', 
                '|', 
                'bold', 
                'italic', 
                'link', 
                'imageUpload',  // Добавляем кнопку загрузки изображений
                '|',
                'bulletedList', 
                'numberedList', 
                '|', 
                'outdent', 
                'indent', 
                '|', 
                'blockQuote', 
                'insertTable', 
                'undo', 
                'redo'
            ],
            language: 'uk',
            // Конфигурация загрузки изображений
            ckfinder: {
                uploadUrl: '/upload-image'
            }
        })
        .then(newEditor => {
            editor = newEditor;
        })
        .catch(error => {
            console.error(error);
        });

    // Обработка отправки формы
    const form = document.querySelector('form');
    form.addEventListener('submit', function(e) {
        // Если редактор инициализирован, обновляем textarea
        if (editor) {
            const descriptionTextarea = document.querySelector('#description');
            const description = editor.getData();
            descriptionTextarea.value = description;
            
            // Проверяем, что описание не пустое
            if (!description.trim()) {
                e.preventDefault();
                alert('Будь ласка, введіть опис розпорядження');
                return false;
            }
        }
    });
}); 