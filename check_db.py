from database import Session
from models import User, Brand, Material, Category, Test, TestQuestion, TestAnswer, TestResult, TestQuestionResult

def check_database():
    session = Session()
    try:
        # Проверяем таблицу users
        users = session.query(User).all()
        print("\nUsers:")
        for user in users:
            print(f"- {user.username} (ID: {user.id}, Role: {user.role})")

        # Проверяем таблицу brands
        brands = session.query(Brand).all()
        print("\nBrands:")
        for brand in brands:
            print(f"- {brand.name} (ID: {brand.id})")

        # Проверяем таблицу categories
        categories = session.query(Category).all()
        print("\nCategories:")
        for category in categories:
            print(f"- {category.name} (ID: {category.id})")

        # Проверяем таблицу materials
        materials = session.query(Material).all()
        print("\nMaterials:")
        for material in materials:
            print(f"- {material.title} (ID: {material.id}, Brand: {material.brand_id})")

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    check_database() 