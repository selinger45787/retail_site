import json
from datetime import datetime
from app import app, db
from models import Brand, Material, User, Test, TestQuestion, TestAnswer, Category, MaterialImage

def import_data_from_json():
    """Импортируем данные из JSON файла в базу данных"""
    try:
        with open('database_export.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        with app.app_context():
            print("=== НАЧАЛО ИМПОРТА ДАННЫХ ===")
            
            # Очищаем существующие данные (кроме таблиц с результатами тестов)
            print("Очистка существующих данных...")
            TestAnswer.query.delete()
            TestQuestion.query.delete()
            Test.query.delete()
            MaterialImage.query.delete()
            Material.query.delete()
            Brand.query.delete()
            Category.query.delete()
            # Не удаляем пользователей, только обновляем существующих
            
            db.session.commit()
            print("Существующие данные очищены")
            
            # Импортируем категории
            print("Импорт категорий...")
            for cat_data in data.get('categories', []):
                category = Category(
                    id=cat_data['id'],
                    name=cat_data['name']
                )
                db.session.add(category)
            db.session.commit()
            print(f"Импортировано категорий: {len(data.get('categories', []))}")
            
            # Импортируем бренды
            print("Импорт брендов...")
            for brand_data in data.get('brands', []):
                brand = Brand(
                    id=brand_data['id'],
                    name=brand_data['name'],
                    image_path=brand_data.get('image_path'),
                    created_at=datetime.fromisoformat(brand_data['created_at']) if brand_data.get('created_at') else datetime.utcnow()
                )
                db.session.add(brand)
            db.session.commit()
            print(f"Импортировано брендов: {len(data.get('brands', []))}")
            
            # Импортируем материалы
            print("Импорт материалов...")
            for material_data in data.get('materials', []):
                material = Material(
                    id=material_data['id'],
                    title=material_data['title'],
                    description=material_data.get('description'),
                    image_path=material_data.get('image_path'),
                    date=datetime.fromisoformat(material_data['date']) if material_data.get('date') else datetime.utcnow(),
                    brand_id=material_data['brand_id'],
                    category_id=material_data['category_id']
                )
                db.session.add(material)
            db.session.commit()
            print(f"Импортировано материалов: {len(data.get('materials', []))}")
            
            # Импортируем изображения материалов
            print("Импорт изображений материалов...")
            for img_data in data.get('material_images', []):
                material_image = MaterialImage(
                    id=img_data['id'],
                    image_path=img_data['image_path'],
                    material_id=img_data['material_id'],
                    created_at=datetime.fromisoformat(img_data['created_at']) if img_data.get('created_at') else datetime.utcnow()
                )
                db.session.add(material_image)
            db.session.commit()
            print(f"Импортировано изображений материалов: {len(data.get('material_images', []))}")
            
            # Импортируем тесты
            print("Импорт тестов...")
            for test_data in data.get('tests', []):
                test = Test(
                    id=test_data['id'],
                    material_id=test_data['material_id'],
                    created_at=datetime.fromisoformat(test_data['created_at']) if test_data.get('created_at') else datetime.utcnow(),
                    is_active=test_data.get('is_active', True)
                )
                db.session.add(test)
            db.session.commit()
            print(f"Импортировано тестов: {len(data.get('tests', []))}")
            
            # Импортируем вопросы тестов
            print("Импорт вопросов тестов...")
            for question_data in data.get('test_questions', []):
                question = TestQuestion(
                    id=question_data['id'],
                    test_id=question_data['test_id'],
                    text=question_data['text'],
                    correct_answer=question_data['correct_answer'],
                    created_at=datetime.fromisoformat(question_data['created_at']) if question_data.get('created_at') else datetime.utcnow()
                )
                db.session.add(question)
            db.session.commit()
            print(f"Импортировано вопросов тестов: {len(data.get('test_questions', []))}")
            
            # Импортируем ответы на вопросы
            print("Импорт ответов на вопросы...")
            for answer_data in data.get('test_answers', []):
                answer = TestAnswer(
                    id=answer_data['id'],
                    question_id=answer_data['question_id'],
                    text=answer_data['text'],
                    created_at=datetime.fromisoformat(answer_data['created_at']) if answer_data.get('created_at') else datetime.utcnow()
                )
                db.session.add(answer)
            db.session.commit()
            print(f"Импортировано ответов на вопросы: {len(data.get('test_answers', []))}")
            
            # Импортируем/обновляем пользователей (кроме admin, которого мы уже создали)
            print("Импорт пользователей...")
            imported_users = 0
            for user_data in data.get('users', []):
                # Пропускаем пользователей с username 'admin'
                if user_data['username'] == 'admin':
                    continue
                    
                # Проверяем, существует ли пользователь
                existing_user = User.query.filter_by(username=user_data['username']).first()
                if not existing_user:
                    user = User(
                        username=user_data['username'],
                        password_hash=user_data['password_hash'],
                        role=user_data.get('role', 'user'),
                        phone_number=user_data.get('phone_number'),
                        department=user_data.get('department', 'other'),
                        position=user_data.get('position', 'other_position'),
                        photo_path=user_data.get('photo_path'),
                        created_at=datetime.fromisoformat(user_data['created_at']) if user_data.get('created_at') else datetime.utcnow()
                    )
                    db.session.add(user)
                    imported_users += 1
            
            db.session.commit()
            print(f"Импортировано новых пользователей: {imported_users}")
            
            print("\n=== ИМПОРТ ЗАВЕРШЕН УСПЕШНО ===")
            print("Все данные были успешно импортированы в базу данных!")
            
    except Exception as e:
        print(f"Ошибка при импорте данных: {str(e)}")
        db.session.rollback()
        raise

if __name__ == '__main__':
    import_data_from_json() 