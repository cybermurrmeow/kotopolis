from app import app, db
from models import AdoptionRequest, Cat
from datetime import date, timedelta
import random

def create_new_requests():
    with app.app_context():
        # Удаляем все существующие заявки (если нужно раскомментировать)
        # AdoptionRequest.query.delete()
        # db.session.commit()
        
        # Получаем всех котов
        cats = Cat.query.all()
        
        if not cats:
            print("❌ Нет котов в базе! Сначала добавьте котов.")
            return
        
        print(f"📊 Доступно котов: {len(cats)}")
        
        # Список новых заявок (статусы: На рассмотрении, Отклонена, Завершена)
        # Нет ни одной заявки со статусом "Одобрена"
        test_requests = [
            {
                "adopter_name": "Анна Петрова",
                "phone": "+7 916 123-45-67",
                "email": "anna.petrova@example.com",
                "comment": "Очень хочу забрать этого котика! У меня есть опыт содержания кошек. Живу в просторной квартире, есть балкон.",
                "status": "На рассмотрении",
                "request_date": date.today() - timedelta(days=1)
            },
            {
                "adopter_name": "Михаил Иванов",
                "phone": "+7 925 987-65-43",
                "email": "mikhail.ivanov@example.com",
                "comment": "Ищу друга для своей дочери. У нас большая квартира, есть все необходимое для кота.",
                "status": "На рассмотрении",
                "request_date": date.today() - timedelta(days=2)
            },
            {
                "adopter_name": "Екатерина Смирнова",
                "phone": "+7 903 555-12-34",
                "email": "ekaterina@example.com",
                "comment": "Уже есть один кот, ищем ему друга. Оба стерилизованы, привиты.",
                "status": "Отклонена",
                "request_date": date.today() - timedelta(days=5)
            },
            {
                "adopter_name": "Дмитрий Козлов",
                "phone": "+7 909 777-88-99",
                "email": "dmitry.kozlov@example.com",
                "comment": "Живу в частном доме, есть большой участок. Кот будет на свободном выгуле.",
                "status": "На рассмотрении",
                "request_date": date.today() - timedelta(days=3)
            },
            {
                "adopter_name": "Ольга Новикова",
                "phone": "+7 915 444-55-66",
                "email": "olga.novikova@example.com",
                "comment": "Хочу взять котика для души. Живу одна, работаю на дому, смогу уделять много внимания.",
                "status": "Завершена",
                "request_date": date.today() - timedelta(days=7)
            },
            {
                "adopter_name": "Сергей Васильев",
                "phone": "+7 926 111-22-33",
                "email": "sergey.vasiliev@example.com",
                "comment": "Ищем компаньона для нашего сына. Обещаем заботу и любовь.",
                "status": "На рассмотрении",
                "request_date": date.today() - timedelta(days=2)
            },
            {
                "adopter_name": "Татьяна Морозова",
                "phone": "+7 912 333-44-55",
                "email": "tatiana.morozova@example.com",
                "comment": "Очень понравился котик! Живу в загородном доме, есть веранда.",
                "status": "Отклонена",
                "request_date": date.today() - timedelta(days=4)
            },
            {
                "adopter_name": "Алексей Кузнецов",
                "phone": "+7 921 666-77-88",
                "email": "alexey.kuznetsov@example.com",
                "comment": "У нас уже есть кот, ищем ему друга. Есть отдельная комната для животных.",
                "status": "На рассмотрении",
                "request_date": date.today() - timedelta(days=1)
            },
            {
                "adopter_name": "Мария Федорова",
                "phone": "+7 904 222-33-44",
                "email": "maria.fedorova@example.com",
                "comment": "Живу в квартире, есть всё для комфортного содержания. Готова стерилизовать и прививать.",
                "status": "На рассмотрении",
                "request_date": date.today() - timedelta(days=3)
            },
            {
                "adopter_name": "Игорь Соколов",
                "phone": "+7 917 888-99-00",
                "email": "igor.sokolov@example.com",
                "comment": "Опыт содержания кошек более 10 лет. Есть свой дом, большая территория.",
                "status": "Завершена",
                "request_date": date.today() - timedelta(days=6)
            }
        ]
        
        # Создаём заявки для разных котов
        added = 0
        for i, request_data in enumerate(test_requests):
            # Выбираем кота по индексу (по кругу)
            cat = cats[i % len(cats)]
            
            # Проверяем, нет ли уже такой заявки
            existing = AdoptionRequest.query.filter_by(
                cat_id=cat.id,
                email=request_data["email"]
            ).first()
            
            if not existing:
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
        print(f"✅ Создано {added} новых заявок!")
        print(f"📊 Всего заявок в базе: {AdoptionRequest.query.count()}")
        print("="*50)
        
        # Показываем статистику по статусам
        print("\n📊 СТАТИСТИКА ЗАЯВОК:")
        for status in ['На рассмотрении', 'Одобрена', 'Отклонена', 'Завершена']:
            count = AdoptionRequest.query.filter_by(status=status).count()
            print(f"   {status}: {count}")

if __name__ == "__main__":
    create_new_requests()