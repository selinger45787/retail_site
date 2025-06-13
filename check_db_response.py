import requests
import json

try:
    response = requests.get("http://localhost:5001/api/test-db", timeout=10)
    print(f"Статус: {response.status_code}")
    print(f"Заголовки: {dict(response.headers)}")
    print(f"Текст ответа: {response.text}")
    
    try:
        data = response.json()
        print(f"JSON данные: {json.dumps(data, indent=2)}")
    except:
        print("Ответ НЕ в JSON формате")
        
except Exception as e:
    print(f"Ошибка: {e}") 