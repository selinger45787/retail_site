#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Скрипт для исправления дублированных функций в app.py

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Удаляем строки с дублированными функциями (начиная с линии 2348)
# Оставляем только первые 2347 строк и добавляем правильное завершение
fixed_lines = lines[:2347]

# Добавляем функции категорий в правильном месте
category_routes = '''
@app.route('/category/<int:category_id>')
def category(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Количество материалов на странице
    
    # Получаем материалы с пагинацией, сортируем по дате в обратном порядке
    materials_pagination = Material.query.filter_by(category_id=category_id)\\
        .order_by(Material.id.desc())\\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    # Получаем все бренды для фильтрации
    brands = Brand.query.all()
    
    return render_template('category.html', 
                         category=category, 
                         materials=materials_pagination.items,
                         pagination=materials_pagination,
                         brands=brands)

@app.route('/category/<int:category_id>/add_material', methods=['GET', 'POST'])
@login_required
def add_material_to_category(category_id):
    if current_user.role != 'admin':
        flash('У вас немає прав для додавання матеріалів', 'error')
        return redirect(url_for('category', category_id=category_id))
    
    category = Category.query.get_or_404(category_id)
    brands = Brand.query.all()
    
    if request.method == 'POST':
        title = request.form.get('title')
        raw_description = request.form.get('description') or ''
        description = unescape(raw_description)
        brand_id = request.form.get('brand_id')
        main_image = request.files.get('image')
        additional_images = request.files.getlist('additional_images')
        
        if not all([title, description, brand_id]):
            flash('Будь ласка, заповніть всі обов\\'язкові поля', 'error')
            return redirect(url_for('add_material_to_category', category_id=category_id))
        
        try:
            # Сохраняем главное изображение
            main_image_path = None
            if main_image and main_image.filename:
                filename = secure_filename(main_image.filename)
                image_path = os.path.join(app.static_folder, 'img', 'materials', filename)
                main_image.save(image_path)
                main_image_path = filename
            
            # Создаем новый материал
            material = Material(
                title=title,
                description=description,
                image_path=main_image_path,
                brand_id=brand_id,
                category_id=category_id
            )
            
            db.session.add(material)
            db.session.flush()
            
            # Сохраняем дополнительные изображения
            for image in additional_images:
                if image and image.filename:
                    filename = secure_filename(image.filename)
                    image_path = os.path.join(app.static_folder, 'img', 'materials', filename)
                    image.save(image_path)
                    
                    material_image = MaterialImage(
                        image_path=filename,
                        material_id=material.id
                    )
                    db.session.add(material_image)
            
            db.session.commit()
            flash('Матеріал успішно додано', 'success')
            return redirect(url_for('category', category_id=category_id))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Ошибка при сохранении материала: {str(e)}")
            flash('Помилка при додаванні матеріалу', 'error')
            return redirect(url_for('add_material_to_category', category_id=category_id))
    
    return render_template('material_add_to_category.html', 
                         category=category,
                         brands=brands)

if __name__ == '__main__':
    app.run(debug=True)
'''

# Добавляем новый код
fixed_lines.append(category_routes)

# Сохраняем исправленный файл
with open('app_fixed.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("Файл исправлен и сохранен как app_fixed.py") 