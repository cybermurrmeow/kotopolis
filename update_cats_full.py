from app import app, db
from models import Cat

def update_cats():
    with app.app_context():
        # Полная информация для всех 20 котов
        cats_info = {
            "Барсик": {
                "personality": "Игривый, любознательный, ласковый, энергичный",
                "activity_level": "Высокий — нужны активные игры каждый день, обожает бегать и прыгать",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": False,
                "favorite_place": "Окно — любит наблюдать за птичками и прохожими",
                "vocal": "Разговорчивый — часто 'разговаривает' с хозяином",
                "food_preferences": "Сухой корм премиум-класса, любит курицу",
                "story": "Барсик был найден на улице в возрасте 2 месяцев в коробке возле подъезда. Его спасли волонтёры.",
                "adoption_recommendation": "Идеальный кот для активной семьи с детьми. Не рекомендуется заводить собаку."
            },
            "Мурка": {
                "personality": "Ласковый, спокойный, нежный, флегматичный",
                "activity_level": "Низкий — любит спать, наблюдать и получать ласку",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Мягкий диван или кресло — обожает уютные уголки",
                "vocal": "Молчаливый — мяукает только когда хочет есть",
                "food_preferences": "Гипоаллергенный корм, не переносит курицу",
                "story": "Мурку привезли в приют, когда её хозяйка переехала в другой город и не смогла взять кошку.",
                "adoption_recommendation": "Идеальный компаньон для пожилых людей или спокойной семьи."
            },
            "Рыжик": {
                "personality": "Энергичный, весёлый, общительный, непоседливый",
                "activity_level": "Очень высокий — нужно много пространства для игр и бега",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Коробка — может часами играть с обычной коробкой",
                "vocal": "Разговорчивый — любит 'петь' по утрам",
                "food_preferences": "Влажный корм, любит рыбу",
                "story": "Рыжика подкинули в приют в коробке в возрасте 2 месяцев.",
                "adoption_recommendation": "Идеальный кот для семьи с детьми. Подойдёт для дома с другими животными."
            },
            "Софи": {
                "personality": "Спокойный, умный, независимый, интеллигентный",
                "activity_level": "Средний — любит играть, но не навязывается",
                "kids_friendly": False,
                "cats_friendly": True,
                "dogs_friendly": False,
                "favorite_place": "Высокая лежанка у окна — любит смотреть сверху",
                "vocal": "Молчаливый — почти никогда не мяукает",
                "food_preferences": "Сухой корм премиум-класса, любит рыбу",
                "story": "Софи жила с пожилой хозяйкой, которая попала в дом престарелых. Кошка осталась одна.",
                "adoption_recommendation": "Только для взрослых, без детей до 14 лет."
            },
            "Тимофей": {
                "personality": "Добрый, умный, игривый, дружелюбный",
                "activity_level": "Высокий — нужно много пространства для игр",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Всюду — особенно любит высоту, может забраться на шкаф",
                "vocal": "Поющий — издаёт мелодичные звуки",
                "food_preferences": "Всё ест, особенно любит мясо",
                "story": "Тимофея нашли на улице в тяжёлом состоянии. Мы его вылечили, сделали операцию.",
                "adoption_recommendation": "Идеальный кот для большой семьи с детьми. Нуждается в регулярном вычёсывании."
            },
            "Люся": {
                "personality": "Общительный, ласковый, любопытный, контактный",
                "activity_level": "Средний — любит играть, но и поспать не прочь",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Под одеялом или на руках — обожает тепло",
                "vocal": "Разговорчивый — любит 'беседовать' с хозяином",
                "food_preferences": "Специальный корм для сфинксов",
                "story": "Люсю отдали в приют из-за аллергии у хозяина.",
                "adoption_recommendation": "Люся подойдёт для семьи, готовой к особому уходу. Нужно регулярное купание."
            },
            "Пушок": {
                "personality": "Спокойный, добрый, ласковый, флегматичный",
                "activity_level": "Низкий — любит спать и есть",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": False,
                "favorite_place": "Тёплая лежанка у батареи",
                "vocal": "Молчаливый — мяукает только когда просит еду",
                "food_preferences": "Лечебный корм для кошек с проблемами мочевыводящей системы",
                "story": "Хозяин Пушка умер, и кот остался один. Соседи принесли его в приют.",
                "adoption_recommendation": "Пушок ищет спокойный дом без собак и маленьких детей."
            },
            "Джесси": {
                "personality": "Активный, любопытный, дружелюбный",
                "activity_level": "Высокий — обожает лазать и исследовать",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Высота — верхние полки, шкафы",
                "vocal": "Разговорчивый — любит 'рассказывать' о своих открытиях",
                "food_preferences": "Сухой корм, любит рыбу",
                "story": "Джесси уже усыновлена! Её взяла семья с двумя детьми.",
                "adoption_recommendation": "Джесси уже нашла свой дом!"
            },
            "Маркиз": {
                "personality": "Сдержанный, умный, спокойный, аристократичный",
                "activity_level": "Средний — любит играть, но без фанатизма",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Коробка — может часами сидеть в коробке",
                "vocal": "Молчаливый — почти не мяукает",
                "food_preferences": "Сухой корм премиум-класс",
                "story": "Маркиза отдали в приют, когда хозяева уехали за границу.",
                "adoption_recommendation": "Маркиз подойдёт для любой семьи. Он спокоен, не шалит."
            },
            "Боня": {
                "personality": "Нежный, игривый, ласковый, маленькое чудо",
                "activity_level": "Высокий — обожает играть и бегать",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "На руках у хозяина",
                "vocal": "Поющий — издаёт мелодичные звуки",
                "food_preferences": "Молочная каша, влажный корм для котят",
                "story": "Боня родилась в приюте. Её маму нашли на улице беременной.",
                "adoption_recommendation": "Боня подойдёт для семьи с детьми. Нуждается в вакцинации."
            },
            "Снежок": {
                "personality": "Нежный, спокойный, пугливый, ласковый",
                "activity_level": "Низкий — любит наблюдать, а не играть",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": False,
                "favorite_place": "Окно — может часами смотреть на улицу",
                "vocal": "Молчаливый — почти не мяукает",
                "food_preferences": "Сухой корм, любит курицу",
                "story": "Снежка была найдена на улице в сильный мороз. Её отогрели, вылечили.",
                "adoption_recommendation": "Снежок подойдёт для спокойной семьи без собак."
            },
            "Шерхан": {
                "personality": "Активный, умный, сильный, лидер",
                "activity_level": "Очень высокий — нужны активные игры каждый день",
                "kids_friendly": True,
                "cats_friendly": False,
                "dogs_friendly": False,
                "favorite_place": "Везде — исследует каждый угол",
                "vocal": "Разговорчивый — любит 'рассказывать' о приключениях",
                "food_preferences": "Мясо, премиальный корм",
                "story": "Шерхана купили как породистого кота, но хозяева не справились с его энергией.",
                "adoption_recommendation": "Шерхан подойдёт только для активных людей. Не рекомендуется для семей с другими животными."
            },
            "Карамелька": {
                "personality": "Любопытный, энергичный, дружелюбный",
                "activity_level": "Высокий — нужны активные игры",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Высота — верхние полки, шкафы",
                "vocal": "Разговорчивый — любит 'беседовать'",
                "food_preferences": "Сухой корм, любит рыбу",
                "story": "Карамелька родилась в приюте. Её мама была подобрана на улице.",
                "adoption_recommendation": "Карамелька подойдёт для активной семьи с детьми."
            },
            "Граф": {
                "personality": "Спокойный, элегантный, умный, аристократ",
                "activity_level": "Низкий — любит отдыхать",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Диван — любит отдыхать в уюте",
                "vocal": "Молчаливый — почти не мяукает",
                "food_preferences": "Сухой корм премиум-класс",
                "story": "Графа отдали в приют, когда хозяин попал в дом престарелых.",
                "adoption_recommendation": "Граф подойдёт для любой семьи. Он спокоен, не шалит."
            },
            "Зефирка": {
                "personality": "Ласковый, игривый, необычный, любит воду",
                "activity_level": "Средний — любит играть и исследовать",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Вода — может часами играть с водой",
                "vocal": "Поющий — издаёт мелодичные звуки",
                "food_preferences": "Влажный корм, любит рыбу",
                "story": "Зефирку привезли в приют из дома, где были аллергики.",
                "adoption_recommendation": "Зефирка подойдёт для семьи с чувством юмора. Если вы готовы к её водным приключениям — она ваша!"
            },
            "Мартин": {
                "personality": "Энергичный, весёлый, дружелюбный, ураган",
                "activity_level": "Очень высокий — нужно много движения",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Бегать — носится по квартире как ураган",
                "vocal": "Разговорчивый — любит 'рассказывать'",
                "food_preferences": "Всё ест, особенно любит курицу",
                "story": "Мартина нашли в подъезде. Он был худым и замёрзшим.",
                "adoption_recommendation": "Мартин подойдёт для активной семьи с детьми. Хорошо ладит с собаками."
            },
            "Леди": {
                "personality": "Ласковый, спокойный, нежный, леди",
                "activity_level": "Низкий — любит отдыхать",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "На руках у хозяина",
                "vocal": "Молчаливый — почти не мяукает",
                "food_preferences": "Сухой корм премиум-класс",
                "story": "Леди уже усыновлена! Она живёт в любящей семье.",
                "adoption_recommendation": "Леди уже нашла свой дом!"
            },
            "Тоша": {
                "personality": "Спокойный, добрый, любит поесть, толстячок",
                "activity_level": "Низкий — любит спать",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Спать — может спать часами",
                "vocal": "Молчаливый — мяукает только когда просит еду",
                "food_preferences": "Диетический корм для снижения веса",
                "story": "Хозяин Тоши умер, и кот остался один.",
                "adoption_recommendation": "Тоша подойдёт для спокойной семьи. Ему нужна диета."
            },
            "Симба": {
                "personality": "Игривый, дружелюбный, ласковый, маленький лев",
                "activity_level": "Высокий — нужно много места для игр",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Игры — обожает активные развлечения",
                "vocal": "Поющий — издаёт мелодичные звуки",
                "food_preferences": "Мясо, премиальный корм",
                "story": "Симбу нашли на улице. Он был истощён и замёрз.",
                "adoption_recommendation": "Симба подойдёт для большой семьи с детьми. Нуждается в регулярном вычёсывании."
            },
            "Жозефина": {
                "personality": "Нежный, ласковый, разговорчивый, тёплая",
                "activity_level": "Средний — любит играть, но не навязывается",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Под одеялом — обожает тепло",
                "vocal": "Разговорчивый — любит 'беседовать'",
                "food_preferences": "Специальный корм для сфинксов",
                "story": "Жозефину отдали в приют из-за аллергии у хозяина.",
                "adoption_recommendation": "Жозефина подойдёт для семьи, готовой к особому уходу. Нужно регулярное купание."
            }
        }
        
        # Обновляем каждого кота
        updated = 0
        for name, info in cats_info.items():
            cat = Cat.query.filter_by(name=name).first()
            if cat:
                cat.personality = info["personality"]
                cat.activity_level = info["activity_level"]
                cat.kids_friendly = info["kids_friendly"]
                cat.cats_friendly = info["cats_friendly"]
                cat.dogs_friendly = info["dogs_friendly"]
                cat.favorite_place = info["favorite_place"]
                cat.vocal = info["vocal"]
                cat.food_preferences = info["food_preferences"]
                cat.story = info["story"]
                cat.adoption_recommendation = info["adoption_recommendation"]
                updated += 1
                print(f"✅ Обновлён: {name}")
            else:
                print(f"⚠️ Не найден: {name}")
        
        db.session.commit()
        
        print("\n" + "="*50)
        print(f"✅ Обновлено {updated} котиков!")
        print("="*50)

if __name__ == "__main__":
    update_cats()