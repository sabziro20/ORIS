# Task Manager (PyQt6)

Небольшое desktop-приложение для создания задач.

## Запуск

```
pip install PyQt6
python main.py
```

## Как пользоваться

1. Введите название задачи (поле Task).
2. Напишите описание.
3. Выберите приоритет: Low, Medium или High.
4. Отметьте нужные настройки: Important, Send notification.
5. Нажмите **Create task** — информация о задаче появится в консоли.

## Используемые виджеты и layouts

| Элемент | Зачем |
|---|---|
| QMainWindow + центральный QWidget | Главное окно; layout вешается на центральный виджет |
| QLineEdit | Однострочное название задачи |
| QTextEdit | Многострочное описание |
| QRadioButton | Выбор одного приоритета |
| QCheckBox | Независимые дополнительные настройки |
| QPushButton (signal `clicked`) | Создание задачи |
| QVBoxLayout | Основная вертикальная компоновка |
| QHBoxLayout | Строки «Task» и «Priority» |
