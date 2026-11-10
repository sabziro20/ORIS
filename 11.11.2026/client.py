import requests

BASE_URL = "http://127.0.0.1:5000"

print("--- 1. Создаем заметки ---")
r = requests.post(f"{BASE_URL}/notes", json={"author": "Ivan", "text": "Первая заметка!"})
print("Создание (Ivan):", r.status_code, r.json())  # Ожидаем 201

r = requests.post(f"{BASE_URL}/notes", json={"author": "Anna", "text": "Привет от Анны"})
print("Создание (Anna):", r.status_code, r.json())  # Ожидаем 201

r = requests.post(f"{BASE_URL}/notes", json={"author": "Ivan", "text": "Вторая заметка от Ивана"})
note_ivan_2_id = r.json().get("id")
print("Создание (Ivan 2):", r.status_code, r.json()) # Ожидаем 201

r = requests.post(f"{BASE_URL}/notes", json={"text": "Без автора"})
print("Создание без автора (Ошибка):", r.status_code, r.json())  # Ожидаем 400


print("\n--- 2. Лайки ---")
r = requests.post(f"{BASE_URL}/notes/{note_ivan_2_id}/like")
print("Лайк Ивану:", r.status_code, r.json()) # Ожидаем 200 и likes = 1

r = requests.post(f"{BASE_URL}/notes/{note_ivan_2_id}/like")
print("Второй лайк Ивану:", r.status_code, r.json()) # Ожидаем 200 и likes = 2

r = requests.post(f"{BASE_URL}/notes/999/like")
print("Лайк несуществующей заметке:", r.status_code, r.json()) # Ожидаем 404


print("\n--- 3. Сортировка и пагинация ---")
r = requests.get(f"{BASE_URL}/notes?sort=likes&order=desc")
print("Список (сортировка по лайкам убыв.):", r.status_code)
for n in r.json():
    print(f"  - [{n['likes']} лайков] {n['author']}: {n['text']}")

r = requests.get(f"{BASE_URL}/notes?sort=magic")
print("Список с кривой сортировкой:", r.status_code, r.json()) # Ожидаем 400


print("\n--- 4. Статистика по авторам ---")
r = requests.get(f"{BASE_URL}/authors")
print("Авторы:", r.status_code, r.json()) # Ожидаем 200 и список статистики


print("\n--- 5. Редактирование (PUT и PATCH) ---")
r = requests.put(f"{BASE_URL}/notes/{note_ivan_2_id}", json={"author": "Ivan The Great", "text": "Обновил целиком!"})
print("PUT:", r.status_code, r.json()) # Ожидаем 200 (лайки должны сохраниться)

r = requests.patch(f"{BASE_URL}/notes/{note_ivan_2_id}", json={"text": "Изменил только текст"})
print("PATCH:", r.status_code, r.json()) # Ожидаем 200


print("--- 6. Массовое удаление ---")
r = requests.delete(f"{BASE_URL}/notes")
print("Массовое удаление без указания автора:", r.status_code, r.json()) # Ожидаем 400

r = requests.delete(f"{BASE_URL}/notes?author=Ivan The Great")
print("Удаляем 'Ivan The Great':", r.status_code, r.json()) # Ожидаем 200, deleted: 1

r = requests.delete(f"{BASE_URL}/notes?author=Nobody")
print("Удаляем 'Nobody' (несуществующего):", r.status_code, r.json()) # Ожидаем 200, deleted: 0


print("\n--- 7. Финальный список ---")
r = requests.get(f"{BASE_URL}/notes")
print("Оставшиеся заметки:", r.status_code, r.json()) # Должна остаться Анна и первая заметка Ивана