document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM загружен, инициализация формы...');
    
    const form = document.getElementById('addMaterialForm');
    const imageInput = document.getElementById('image');
    const imagePreview = document.getElementById('imagePreview');
    let editor = null;

    console.log('Форма найдена:', form);
    console.log('Поля формы:', {
        title: document.getElementById('title'),
        category: document.getElementById('category_id'),
        description: document.getElementById('description'),
        image: imageInput
    });

    // Инициализация CKEditor
    ClassicEditor
        .create(document.querySelector('#description'), {
            toolbar: [
                'heading', '|',
                'bold', 'italic', 'link', 'bulletedList', 'numberedList', '|',
                'sourceEditing', '|',  // Добавляем кнопку Source Editing
                'undo', 'redo'
            ],
            placeholder: 'Введіть опис матеріалу...',
            extraPlugins: [SourceEditing]  // Подключаем плагин Source Editing
        })
        .then(newEditor => {
            console.log('CKEditor успешно инициализирован');
            editor = newEditor;
            
            // Добавляем слушатель изменений
            editor.model.document.on('change:data', () => {
                const data = editor.getData();
                console.log('Текущее содержимое редактора:', data);
                // Обновляем значение textarea
                document.getElementById('description').value = data;
            });
        })
        .catch(error => {
            console.error('Ошибка при инициализации CKEditor:', error);
        });

    // Обработка отправки формы
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        console.log('Форма отправляется...');
        
        // Проверяем, инициализирован ли редактор
        if (!editor) {
            console.error('Редактор еще не инициализирован');
            alert('Будь ласка, зачекайте поки редактор завантажиться');
            return;
        }
        
        // Получаем данные из CKEditor
        const description = editor.getData();
        console.log('Данные из CKEditor перед отправкой:', description);
        
        // Проверяем все обязательные поля
        const title = document.getElementById('title').value;
        const categoryId = document.getElementById('category_id').value;
        const brandId = document.getElementById('brand_id') ? document.getElementById('brand_id').value : null;
        
        console.log('Form data before submit:', {
            title,
            description,
            categoryId,
            brandId
        });
        
        // Если все поля заполнены, отправляем форму
        if (title && description && categoryId && (brandId || !document.getElementById('brand_id'))) {
            // Устанавливаем значение из редактора в textarea
            document.getElementById('description').value = description;
            console.log('Submitting form with description:', document.getElementById('description').value);
            form.submit();
        } else {
            alert('Будь ласка, заповніть всі обов\'язкові поля');
        }
    });

    // Предпросмотр изображения
    imageInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
            }
            reader.readAsDataURL(file);
        } else {
            imagePreview.innerHTML = '';
        }
    });
}); 