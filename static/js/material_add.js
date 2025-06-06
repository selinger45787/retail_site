// JavaScript for material_add.html

// Add your custom scripts here

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM загружен, инициализация формы...');
    
    const form = document.getElementById('addMaterialForm');
    const imageInput = document.getElementById('image');
    const imagePreview = document.getElementById('imagePreview');
    const addImageBtn = document.getElementById('addImageBtn');
    const additionalImagesContainer = document.getElementById('additionalImagesContainer');
    const descriptionTextarea = document.getElementById('description');
    let editor = null;

    console.log('Елементи форми:', {
        form: form,
        imageInput: imageInput,
        imagePreview: imagePreview,
        addImageBtn: addImageBtn,
        additionalImagesContainer: additionalImagesContainer,
        descriptionTextarea: descriptionTextarea
    });

    // Инициализация CKEditor
    DecoupledEditor
        .create(document.querySelector('#editor-container'), {
            language: 'uk',
            toolbar: {
                items: [
                    'heading',
                    '|',
                    'fontSize',
                    'fontFamily',
                    '|',
                    'fontColor',
                    'fontBackgroundColor',
                    '|',
                    'bold',
                    'italic',
                    'underline',
                    'strikethrough',
                    '|',
                    'alignment',
                    '|',
                    'numberedList',
                    'bulletedList',
                    '|',
                    'outdent',
                    'indent',
                    '|',
                    'link',
                    'imageUpload',
                    'blockQuote',
                    'insertTable',
                    '|',
                    'undo',
                    'redo'
                ],
                shouldNotGroupWhenFull: true
            },
            placeholder: 'Введіть опис матеріалу...',
            table: {
                contentToolbar: [
                    'tableColumn',
                    'tableRow',
                    'mergeTableCells'
                ]
            },
            ckfinder: {
                uploadUrl: '/upload-image'
            }
        })
        .then(newEditor => {
            console.log('CKEditor успішно ініціалізовано');
            editor = newEditor;
            
            // Додаємо панель інструментів у контейнер
            const toolbarContainer = document.querySelector('.toolbar-container');
            toolbarContainer.appendChild(editor.ui.view.toolbar.element);
            
            // Додаємо слухач змін
            editor.model.document.on('change:data', () => {
                const data = editor.getData();
                console.log('Вміст редактора оновлено');
                // Оновлюємо приховане поле textarea з даними для відправки форми
                descriptionTextarea.value = data;
            });
        })
        .catch(error => {
            console.error('Помилка при ініціалізації CKEditor:', error);
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
        
        // Получаем данные из CKEditor и обновляем скрытое поле
        const description = editor.getData();
        descriptionTextarea.value = description;
        
        // Проверяем все обязательные поля
        const title = document.getElementById('title').value.trim();
        
        // Получаем category_id из видимого селекта или скрытого поля
        let categoryId = '';
        const categorySelect = document.getElementById('category_id');
        const categoryHidden = document.querySelector('input[name="category_id"]');
        
        if (categorySelect && !categorySelect.disabled) {
            categoryId = categorySelect.value;
        } else if (categoryHidden) {
            categoryId = categoryHidden.value;
        }
        
        const brandId = document.getElementById('brand_id') ? document.getElementById('brand_id').value : null;
        
        console.log('Данные формы перед отправкой:', {
            title,
            description,
            categoryId,
            brandId
        });
        
        // Проверяем заполнение всех обязательных полей
        if (!title) {
            alert('Будь ласка, введіть назву матеріалу');
            return;
        }
        
        if (!description) {
            alert('Будь ласка, введіть опис матеріалу');
            return;
        }
        
        if (!categoryId) {
            alert('Будь ласка, виберіть категорію');
            return;
        }
        
        if (document.getElementById('brand_id') && !brandId) {
            alert('Будь ласка, виберіть бренд');
            return;
        }
        
        // Если все поля заполнены, отправляем форму
        form.submit();
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

    // Добавление нового поля для изображения
    if (addImageBtn) {
        addImageBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const newInput = document.createElement('div');
            newInput.className = 'additional-image-input mb-2';
            newInput.innerHTML = `
                <div class="input-group">
                    <input type="file" class="form-control" name="additional_images" accept="image/*">
                    <button type="button" class="btn btn-danger remove-image">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;
            
            additionalImagesContainer.appendChild(newInput);

            // Добавляем обработчик для кнопки удаления
            const removeBtn = newInput.querySelector('.remove-image');
            if (removeBtn) {
                removeBtn.addEventListener('click', function() {
                    newInput.remove();
                });
            }
        });
    }
}); 