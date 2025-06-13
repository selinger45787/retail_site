#!/usr/bin/env python3
import requests
import json

print("=== ТЕСТ НОВОГО API INVENTORY-REPORT ===")

try:
    response = requests.get('http://localhost:5001/api/inventory-report', timeout=30)
    
    print(f"Статус: {response.status_code}")
    print(f"Заголовки: {dict(response.headers)}")
    print()
    
    if response.status_code == 200:
        data = response.json()
        print("✅ УСПЕШНО!")
        print(f"📊 Получено записей: {len(data.get('records', []))}")
        print(f"📈 Общее количество: {data.get('total_records', 0)}")
        print()
        
        # Показываем первые несколько записей
        records = data.get('records', [])
        if records:
            print("🔍 Первые 3 записи:")
            for i, record in enumerate(records[:3]):
                print(f"\n--- Запись {i+1} ---")
                for key, value in record.items():
                    print(f"{key}: {value}")
        else:
            print("⚠️ Нет записей в ответе")
    else:
        print(f"❌ ОШИБКА {response.status_code}")
        print(f"Ответ: {response.text}")
        
except Exception as e:
    print(f"💥 ИСКЛЮЧЕНИЕ: {e}") 