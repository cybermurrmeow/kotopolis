from app import app, db
from models import AdoptionRequest, Cat
from datetime import date, timedelta
import random

def create_test_requests():
    with app.app_context():
        # Получаем всех котов
        cats = Cat.query.all()
        
        if not cats:
            print("❌ Нет котов в базе! Сначала добавьте котов.")
            return
        
        # Список тестовых заявок
        test_requests = [
            {
                "adopter_name": "Анна Смирнова",
                "phone": "+7 916 123-45-67",
                "email": "anna@example.com",
                "comment": "Очень хочу забрать этого котика! У меня есть опыт содержания кошек. Живу в просторной квартире, есть балкон. Готова приехать в любое время.",
                "status": "На рассмотрении",
                "request_date": date.today() - timedelta(days=1)
            },
            {
                "adopter_name": "Михаил Петров",
                "phone": "+7 925 987-65-43",
                "email": "mikhail@example.com",
                "comment": "Ищу друга для своей дочери. У нас большая квартира, есть все необходимое для кота. Рассчитываю на долгосрочную дружбу.",
                "status": "На рассмотрении",
                "request_date": date.today() - timedelta(days=2)
            },
            {
                "adopter_name": "Елена Козлова",
                "phone": "+7 903 555-12-34",
                "email": "elena@example.com",
                "comment": "Уже есть один кот, ищем ему друга. Оба стерилизованы, привиты. Есть опыт ухода за животными.",
                "status": "Одобрена",
                "request_date": date.today() - timedelta(days=5)
            },
            {
                "adopter_name": "Дмитрий Иванов",
                "phone": "+7 909 777-88-99",
                "email": "dmitry@example.com",
                "comment": "Живу в частном доме, есть большой участок. Кот будет на свободном выгуле. Опыт содержания кошек есть.",
                "status": "Отклонена",
                "request_date": date.today() - timedelta(days=7)
            },
            {
                "adopter_name": "Ольга Новикова",
                "phone": "+7 915 444-55-66",
                "email": "olga@example.com",
                "comment": "Хочу взять котика для души. Живу одна, работаю на дому, смогу уделять много внимания. Готова к любым рекомендациям.",
                "status": "На рассмотрении",
                "request_date": date.today() - timedelta(days=3)
            },
            {
                "adopter_name": "Сергей Васильев",
                "phone": "+7 926 111-22-33",
                "email": "sergey@example.com",
                "comment": "Ищем компаньона для нашего сына 8 лет. Обещаем заботу и любовь. Есть опыт содержания животных.",
                "status": "Завершена",
                "request_date": date.today() - timedelta(days=10)
            },
            {
                "adopter_name": "Татьяна Морозова",
                "phone": "+7 912 333-44-55",
                "email": "tatiana@example.com",
                "comment": "Очень понравился котик! Живу в загородном доме, есть веранда. Готова приехать за ним хоть завтра.",
                "status": "На рассмотрении",
                "request_date": date.today() - timedelta(days=4)
            },
            {
                "adopter_name": "Алексей Кузнецов",
                "phone": "+7 921 666-77-88",
                "email": "alexey@example.com",
                "comment": "У нас уже есть кот, ищем ему друга. Кот стерилизован, привит. Есть отдельная комната для животных.",
                "status": "Одобрена",
                "request_date": date.today() - timedelta(days=6)
            },
            {
                "adopter_name": "Мария Федорова",
                "phone": "+7 904 222-33-44",
                "email": "maria@example.com",
                "comment": "Живу в квартире, есть все для комфортного содержания. Готова стерилизовать и прививать по рекомендациям.",
                "status": "На рассмотрении",
                "request_date": date.today() - timedelta(days=2)
            },
            {
                "adopter_name": "Игорь Соколов",
                "phone": "+7 917 888-99-00",
                "email": "igor@example.com",
                "comment": "Опыт содержания кошек более 10 лет. Есть свой дом, большая территория. Жду встречи!",
                "status": "Отклонена",
                "request_date": date.today() - timedelta(days=8)
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
                print(f"✅ Добавлена заявка от {request_data['adopter_name']} на кота {cat.name}")
        
        db.session.commit()
        
        print("\n" + "="*50)
        print(f"✅ Создано {added} тестовых заявок!")
        print(f"📊 Всего заявок в базе: {AdoptionRequest.query.count()}")
        print("="*50)
        
        # Показываем статистику по статусам
        print("\n📊 СТАТИСТИКА ЗАЯВОК:")
        for status in ['На рассмотрении', 'Одобрена', 'Отклонена', 'Завершена']:
            count = AdoptionRequest.query.filter_by(status=status).count()
            print(f"   {status}: {count}")

if __name__ == "__main__":
    create_test_requests()