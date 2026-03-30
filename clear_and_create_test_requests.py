from app import app, db
from models import AdoptionRequest, Cat
from datetime import date, timedelta
import random

def clear_and_create_test_requests():
    with app.app_context():
        # Удаляем все существующие заявки
        old_count = AdoptionRequest.query.count()
        AdoptionRequest.query.delete()
        db.session.commit()
        print(f"🗑️ Удалено {old_count} старых заявок")
        
        # Получаем всех котов
        cats = Cat.query.all()
        
        if not cats:
            print("❌ Нет котов в базе! Сначала добавьте котов.")
            return
        
        # Список тестовых заявок (вымышленные имена)
        test_requests = [
            {
                "adopter_name": "Мария Иванова",
                "phone": "+7 900 111-22-33",
                "email": "maria@example.com",
                "comment": "Очень понравился котик! Живу в квартире, есть опыт содержания кошек.",
                "status": "На рассмотрении",
                "request_date": date.today() - timedelta(days=1)
            },
            {
                "adopter_name": "Алексей Петров",
                "phone": "+7 901 222-33-44",
                "email": "alexey@example.com",
                "comment": "Ищу друга для дочери. У нас есть всё необходимое для кота.",
                "status": "На рассмотрении",
                "request_date": date.today() - timedelta(days=2)
            },
            {
                "adopter_name": "Елена Смирнова",
                "phone": "+7 902 333-44-55",
                "email": "elena@example.com",
                "comment": "Уже есть один кот, ищем ему друга. Оба стерилизованы, привиты.",
                "status": "Одобрена",
                "request_date": date.today() - timedelta(days=5)
            },
            {
                "adopter_name": "Дмитрий Козлов",
                "phone": "+7 903 444-55-66",
                "email": "dmitry@example.com",
                "comment": "Живу в частном доме, есть большой участок. Кот будет на свободном выгуле.",
                "status": "Отклонена",
                "request_date": date.today() - timedelta(days=7)
            },
            {
                "adopter_name": "Ольга Новикова",
                "phone": "+7 904 555-66-77",
                "email": "olga@example.com",
                "comment": "Хочу взять котика для души. Живу одна, работаю на дому, смогу уделять много внимания.",
                "status": "На рассмотрении",
                "request_date": date.today() - timedelta(days=3)
            },
            {
                "adopter_name": "Сергей Васильев",
                "phone": "+7 905 666-77-88",
                "email": "sergey@example.com",
                "comment": "Ищем компаньона для нашего сына. Обещаем заботу и любовь.",
                "status": "Завершена",
                "request_date": date.today() - timedelta(days=10)
            },
            {
                "adopter_name": "Татьяна Морозова",
                "phone": "+7 906 777-88-99",
                "email": "tatiana@example.com",
                "comment": "Очень понравился котик! Живу в загородном доме, есть веранда.",
                "status": "На рассмотрении",
                "request_date": date.today() - timedelta(days=4)
            },
            {
                "adopter_name": "Игорь Кузнецов",
                "phone": "+7 907 888-99-00",
                "email": "igor@example.com",
                "comment": "У нас уже есть кот, ищем ему друга. Есть отдельная комната для животных.",
                "status": "Одобрена",
                "request_date": date.today() - timedelta(days=6)
            },
            {
                "adopter_name": "Анна Федорова",
                "phone": "+7 908 999-00-11",
                "email": "anna@example.com",
                "comment": "Живу в квартире, есть всё для комфортного содержания. Готова к любым рекомендациям.",
                "status": "На рассмотрении",
                "request_date": date.today() - timedelta(days=2)
            },
            {
                "adopter_name": "Павел Соколов",
                "phone": "+7 909 111-22-33",
                "email": "pavel@example.com",
                "comment": "Опыт содержания кошек более 10 лет. Есть свой дом, большая территория.",
                "status": "Отклонена",
                "request_date": date.today() - timedelta(days=8)
            }
        ]
        
        # Создаём заявки для разных котов
        added = 0
        for i, request_data in enumerate(test_requests):
            # Выбираем кота по индексу (по кругу)
            cat = cats[i % len(cats)]
            
            new_request = AdoptionRequest(
                cat_id=cat.id,
                adopter_name=request_data["adopter_name"],
                phone=request_data["phone"],
                email=request_data["email"],
                comment=request_data["comment"],
                status=request_data["status"],
                request_date=request_data["request_date"]
            )
            db.session.add(new_request)
            added += 1
            print(f"✅ Добавлена заявка от {request_data['adopter_name']} на кота {cat.name} ({request_data['status']})")
        
        db.session.commit()
        
        print("\n" + "="*50)
        print(f"✅ Создано {added} новых тестовых заявок!")
        print(f"📊 Всего заявок в базе: {AdoptionRequest.query.count()}")
        print("="*50)
        
        # Показываем статистику по статусам
        print("\n📊 СТАТИСТИКА ЗАЯВОК:")
        for status in ['На рассмотрении', 'Одобрена', 'Отклонена', 'Завершена']:
            count = AdoptionRequest.query.filter_by(status=status).count()
            print(f"   {status}: {count}")

if __name__ == "__main__":
    clear_and_create_test_requests()