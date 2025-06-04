#!/usr/bin/env python3
"""
Миграция для добавления полей времени в существующую базу данных (PostgreSQL)
"""

from app import app, db
from sqlalchemy import text

def migrate_timing_fields():
    with app.app_context():
        try:
            print("🔄 Добавляем поля времени в таблицу test_result...")
            
            # Проверяем, существуют ли уже поля (для PostgreSQL)
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'test_result'
            """))
            columns = [row[0] for row in result.fetchall()]
            
            print(f"Существующие поля: {columns}")
            
            # Добавляем started_at если его нет
            if 'started_at' not in columns:
                db.session.execute(text("ALTER TABLE test_result ADD COLUMN started_at TIMESTAMP"))
                print("✅ Поле started_at добавлено")
            else:
                print("ℹ️ Поле started_at уже существует")
            
            # Добавляем time_taken если его нет
            if 'time_taken' not in columns:
                db.session.execute(text("ALTER TABLE test_result ADD COLUMN time_taken INTEGER"))
                print("✅ Поле time_taken добавлено")
            else:
                print("ℹ️ Поле time_taken уже существует")
            
            db.session.commit()
            print("🎉 Миграция завершена успешно!")
            
            # Проверяем результат
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'test_result'
                ORDER BY ordinal_position
            """))
            new_columns = [row[0] for row in result.fetchall()]
            print(f"Поля после миграции: {new_columns}")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Ошибка при миграции: {e}")
            return False

if __name__ == "__main__":
    migrate_timing_fields() 