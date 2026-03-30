from app import app, db
from models import Cat
from datetime import date

def update_cats_info():
    with app.app_context():
        # Дополнительная информация для каждого кота
        cats_info = {
            "Барсик": {
                "personality": "Игривый, любознательный, ласковый",
                "activity_level": "Высокий (нужны активные игры каждый день)",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": False,
                "favorite_place": "Окно (любит наблюдать за птичками)",
                "vocal": "Разговорчивый (часто 'разговаривает' с хозяином)",
                "food_preferences": "Сухой корм премиум-класса, любит курицу",
                "story": "Барсик был найден на улице в возрасте 2 месяцев. Его нашли в коробке возле подъезда. С тех пор он вырос в здорового и активного кота. Очень благодарный и привязан к людям.",
                "adoption_recommendation": "Идеальный кот для активной семьи с детьми. Ему нужно много внимания и игр. Не рекомендуется заводить собаку, так как Барсик ревнив и может не поделить внимание."
            },
            "Мурка": {
                "personality": "Ласковый, спокойный, нежный",
                "activity_level": "Низкий (любит спать и наблюдать)",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Мягкий диван или кресло",
                "vocal": "Молчаливый (мяукает только когда хочет есть)",
                "food_preferences": "Гипоаллергенный корм, не переносит курицу",
                "story": "Мурку привезли в приют, когда её хозяйка переехала в другой город и не смогла взять кошку. Мурка очень скучала по дому, но сейчас привыкла и ждёт новую любящую семью.",
                "adoption_recommendation": "Идеальный компаньон для пожилых людей или спокойной семьи. Ей нужно тихое место и правильное питание. Не требует активных игр, но ценит ласку и внимание."
            },
            "Рыжик": {
                "personality": "Энергичный, весёлый, общительный",
                "activity_level": "Очень высокий (нужно много пространства для игр)",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Коробка (может часами играть с обычной коробкой)",
                "vocal": "Разговорчивый (любит 'петь' по утрам)",
                "food_preferences": "Влажный корм, любит рыбу",
                "story": "Рыжика подкинули в приют в коробке. Ему было всего 2 месяца. Сейчас он подрос, но иногда болеет. Мы лечим его ушко, скоро он будет полностью здоров.",
                "adoption_recommendation": "Идеальный кот для семьи с детьми. Ему нужно много активных игр и внимания. Подойдёт для дома с другими животными."
            },
            "Софи": {
                "personality": "Спокойный, умный, независимый",
                "activity_level": "Средний (любит играть, но не навязывается)",
                "kids_friendly": False,
                "cats_friendly": True,
                "dogs_friendly": False,
                "favorite_place": "Высокая лежанка у окна",
                "vocal": "Молчаливый (почти никогда не мяукает)",
                "food_preferences": "Сухой корм, премиум-класс",
                "story": "Софи жила с пожилой хозяйкой, которая попала в дом престарелых. Кошка осталась одна. Она очень привязана к людям, но не переносит маленьких детей и шум.",
                "adoption_recommendation": "Только для взрослых, без детей. Софи ищет спокойный дом и любящего хозяина."
            },
            "Тимофей": {
                "personality": "Добрый, умный, игривый",
                "activity_level": "Высокий (нужно много пространства)",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Всюду, особенно любит высоту",
                "vocal": "Поющий (издаёт мелодичные звуки)",
                "food_preferences": "Всё ест, особенно любит мясо",
                "story": "Тимофея нашли на улице в тяжёлом состоянии. Мы его вылечили, сделали операцию. Сейчас он на карантине, но скоро будет готов к усыновлению.",
                "adoption_recommendation": "Идеальный кот для большой семьи с детьми. Ему нужно много пространства и внимания. Отлично ладит с другими животными."
            },
            "Люся": {
                "personality": "Общительный, ласковый, любопытный",
                "activity_level": "Средний (любит играть, но и поспать не прочь)",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Под одеялом или на руках",
                "vocal": "Разговорчивый (любит 'беседовать')",
                "food_preferences": "Специальный корм для сфинксов",
                "story": "Люсю отдали в приют из-за аллергии у хозяина. Она очень скучает по дому и ищет новую семью.",
                "adoption_recommendation": "Люся подойдёт для семьи, готовой к особому уходу. Нужно регулярное купание и увлажнение кожи."
            },
            "Пушок": {
                "personality": "Спокойный, добрый, ласковый",
                "activity_level": "Низкий (любит спать и есть)",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": False,
                "favorite_place": "Тёплая лежанка у батареи",
                "vocal": "Молчаливый (мяукает только когда просит еду)",
                "food_preferences": "Лечебный корм для кошек с проблемами мочевыводящей системы",
                "story": "Хозяин Пушка умер, и кот остался один. Соседи принесли его в приют.",
                "adoption_recommendation": "Пушок ищет спокойный дом без собак и маленьких детей. Ему нужна диета и регулярное наблюдение у ветеринара."
            },
            "Джесси": {
                "personality": "Активный, любопытный, дружелюбный",
                "activity_level": "Высокий (обожает лазать и исследовать)",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Высота (верхние полки, шкафы)",
                "vocal": "Разговорчивый (любит 'рассказывать' о своих открытиях)",
                "food_preferences": "Сухой корм, любит рыбу",
                "story": "Джесси уже усыновлена! Её взяла семья с двумя детьми.",
                "adoption_recommendation": "Джесси уже нашла свой дом!"
            },
            "Маркиз": {
                "personality": "Сдержанный, умный, спокойный",
                "activity_level": "Средний (любит играть, но без фанатизма)",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Коробка (может часами сидеть в коробке)",
                "vocal": "Молчаливый (почти не мяукает)",
                "food_preferences": "Сухой корм, премиум-класс",
                "story": "Маркиза отдали в приют, когда хозяева уехали за границу.",
                "adoption_recommendation": "Маркиз подойдёт для любой семьи. Он спокоен, не шалит, хорошо ладит с другими животными."
            },
            "Боня": {
                "personality": "Нежный, игривый, ласковый",
                "activity_level": "Высокий (обожает играть и бегать)",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "На руках у хозяина",
                "vocal": "Поющий (издаёт мелодичные звуки)",
                "food_preferences": "Молочная каша, влажный корм для котят",
                "story": "Боня родилась в приюте. Её маму нашли на улице беременной.",
                "adoption_recommendation": "Боня подойдёт для семьи с детьми. Она очень нежная и ласковая. Нуждается в вакцинации."
            },
            "Снежок": {
                "personality": "Нежный, спокойный, пугливый",
                "activity_level": "Низкий (любит наблюдать, а не играть)",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": False,
                "favorite_place": "Окно (может часами смотреть на улицу)",
                "vocal": "Молчаливый (почти не мяукает)",
                "food_preferences": "Сухой корм, любит курицу",
                "story": "Снежка была найдена на улице в сильный мороз. Её отогрели, вылечили.",
                "adoption_recommendation": "Снежок подойдёт для спокойной семьи без собак. Ей нужен уютный дом."
            },
            "Шерхан": {
                "personality": "Активный, умный, сильный",
                "activity_level": "Очень высокий (нужны активные игры каждый день)",
                "kids_friendly": True,
                "cats_friendly": False,
                "dogs_friendly": False,
                "favorite_place": "Везде (исследует каждый угол)",
                "vocal": "Разговорчивый (любит 'рассказывать' о приключениях)",
                "food_preferences": "Мясо, премиальный корм",
                "story": "Шерхана купили как породистого кота, но хозяева не справились с его энергией.",
                "adoption_recommendation": "Шерхан подойдёт только для активных людей. Ему нужно много места для игр."
            },
            "Карамелька": {
                "personality": "Любопытный, энергичный, дружелюбный",
                "activity_level": "Высокий (нужны активные игры)",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Высота (верхние полки, шкафы)",
                "vocal": "Разговорчивый (любит 'беседовать')",
                "food_preferences": "Сухой корм, любит рыбу",
                "story": "Карамелька родилась в приюте. Её мама была подобрана на улице.",
                "adoption_recommendation": "Карамелька подойдёт для активной семьи с детьми. Ей нужно много игрушек."
            },
            "Граф": {
                "personality": "Спокойный, элегантный, умный",
                "activity_level": "Низкий (любит отдыхать)",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Диван (любит отдыхать в уюте)",
                "vocal": "Молчаливый (почти не мяукает)",
                "food_preferences": "Сухой корм, премиум-класс",
                "story": "Графа отдали в приют, когда хозяин попал в дом престарелых.",
                "adoption_recommendation": "Граф подойдёт для любой семьи. Он спокоен, не шалит, хорошо ладит с другими животными."
            },
            "Зефирка": {
                "personality": "Ласковый, игривый, необычный",
                "activity_level": "Средний (любит играть и исследовать)",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Вода (может часами играть с водой)",
                "vocal": "Поющий (издаёт мелодичные звуки)",
                "food_preferences": "Влажный корм, любит рыбу",
                "story": "Зефирку привезли в приют из дома, где были аллергики.",
                "adoption_recommendation": "Зефирка подойдёт для семьи с чувством юмора. Если вы готовы к её водным приключениям — она ваша!"
            },
            "Мартин": {
                "personality": "Энергичный, весёлый, дружелюбный",
                "activity_level": "Очень высокий (нужно много движения)",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Бегать (носится по квартире как ураган)",
                "vocal": "Разговорчивый (любит 'рассказывать')",
                "food_preferences": "Всё ест, особенно любит курицу",
                "story": "Мартина нашли в подъезде. Он был худым и замёрзшим.",
                "adoption_recommendation": "Мартин подойдёт для активной семьи с детьми. Ему нужно много места для игр."
            },
            "Леди": {
                "personality": "Ласковый, спокойный, нежный",
                "activity_level": "Низкий (любит отдыхать)",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "На руках у хозяина",
                "vocal": "Молчаливый (почти не мяукает)",
                "food_preferences": "Сухой корм, премиум-класс",
                "story": "Леди уже усыновлена! Она живёт в любящей семье.",
                "adoption_recommendation": "Леди уже нашла свой дом!"
            },
            "Тоша": {
                "personality": "Спокойный, добрый, любит поесть",
                "activity_level": "Низкий (любит спать)",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Спать (может спать часами)",
                "vocal": "Молчаливый (мяукает только когда просит еду)",
                "food_preferences": "Диетический корм для снижения веса",
                "story": "Хозяин Тоши умер, и кот остался один.",
                "adoption_recommendation": "Тоша подойдёт для спокойной семьи. Ему нужна диета и регулярные прогулки для снижения веса."
            },
            "Симба": {
                "personality": "Игривый, дружелюбный, ласковый",
                "activity_level": "Высокий (нужно много места для игр)",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Игры (обожает активные развлечения)",
                "vocal": "Поющий (издаёт мелодичные звуки)",
                "food_preferences": "Мясо, премиальный корм",
                "story": "Симбу нашли на улице. Он был истощён и замёрз.",
                "adoption_recommendation": "Симба подойдёт для большой семьи с детьми. Ему нужно много места для игр."
            },
            "Жозефина": {
                "personality": "Нежный, ласковый, разговорчивый",
                "activity_level": "Средний (любит играть, но не навязывается)",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Под одеялом (обожает тепло)",
                "vocal": "Разговорчивый (любит 'беседовать')",
                "food_preferences": "Специальный корм для сфинксов",
                "story": "Жозефину отдали в приют из-за аллергии у хозяина.",
                "adoption_recommendation": "Жозефина подойдёт для семьи, готовой к особому уходу. Нужно регулярное купание и увлажнение кожи."
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
                print(f"✅ Обновлена информация: {name}")
            else:
                print(f"⚠️ Кот {name} не найден в базе!")
        
        db.session.commit()
        
        print("\n" + "="*60)
        print(f"✅ Обновлено {updated} котиков!")
        print(f"📊 Всего котиков в базе: {Cat.query.count()}")
        print("="*60)

if __name__ == "__main__":
    update_cats_info()