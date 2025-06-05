import json
from app import app, db
from models import Brand, Material, User, Test, TestQuestion, TestAnswer, Category, MaterialImage

def export_data_to_json():
    """Экспортируем данные из локальной базы в JSON файл"""
    with app.app_context():
        data = {}
        
        # Экспортируем пользователей
        users = User.query.all()
        data['users'] = []
        for user in users:
            data['users'].append({
                'id': user.id,
                'username': user.username,
                'password_hash': user.password_hash,
                'role': user.role,
                'phone_number': user.phone_number,
                'department': user.department,
                'position': user.position,
                'photo_path': user.photo_path,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
        
        # Экспортируем категории
        categories = Category.query.all()
        data['categories'] = []
        for category in categories:
            data['categories'].append({
                'id': category.id,
                'name': category.name
            })
        
        # Экспортируем бренды
        brands = Brand.query.all()
        data['brands'] = []
        for brand in brands:
            data['brands'].append({
                'id': brand.id,
                'name': brand.name,
                'image_path': brand.image_path,
                'created_at': brand.created_at.isoformat() if brand.created_at else None
            })
        
        # Экспортируем материалы
        materials = Material.query.all()
        data['materials'] = []
        for material in materials:
            data['materials'].append({
                'id': material.id,
                'title': material.title,
                'description': material.description,
                'image_path': material.image_path,
                'date': material.date.isoformat() if material.date else None,
                'brand_id': material.brand_id,
                'category_id': material.category_id
            })
        
        # Экспортируем изображения материалов
        material_images = MaterialImage.query.all()
        data['material_images'] = []
        for img in material_images:
            data['material_images'].append({
                'id': img.id,
                'image_path': img.image_path,
                'material_id': img.material_id,
                'created_at': img.created_at.isoformat() if img.created_at else None
            })
        
        # Экспортируем тесты
        tests = Test.query.all()
        data['tests'] = []
        for test in tests:
            data['tests'].append({
                'id': test.id,
                'material_id': test.material_id,
                'created_at': test.created_at.isoformat() if test.created_at else None,
                'is_active': test.is_active
            })
        
        # Экспортируем вопросы тестов
        test_questions = TestQuestion.query.all()
        data['test_questions'] = []
        for question in test_questions:
            data['test_questions'].append({
                'id': question.id,
                'test_id': question.test_id,
                'text': question.text,
                'correct_answer': question.correct_answer,
                'created_at': question.created_at.isoformat() if question.created_at else None
            })
        
        # Экспортируем ответы на вопросы
        test_answers = TestAnswer.query.all()
        data['test_answers'] = []
        for answer in test_answers:
            data['test_answers'].append({
                'id': answer.id,
                'question_id': answer.question_id,
                'text': answer.text,
                'created_at': answer.created_at.isoformat() if answer.created_at else None
            })
        
        # Сохраняем в JSON файл
        with open('database_export.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print("=== СТАТИСТИКА ЭКСПОРТА ===")
        print(f"Пользователи: {len(data['users'])}")
        print(f"Категории: {len(data['categories'])}")
        print(f"Бренды: {len(data['brands'])}")
        print(f"Материалы: {len(data['materials'])}")
        print(f"Изображения материалов: {len(data['material_images'])}")
        print(f"Тесты: {len(data['tests'])}")
        print(f"Вопросы тестов: {len(data['test_questions'])}")
        print(f"Ответы на вопросы: {len(data['test_answers'])}")
        print("\nДанные экспортированы в файл: database_export.json")

if __name__ == '__main__':
    export_data_to_json() 