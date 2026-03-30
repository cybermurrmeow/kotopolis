from app import app, db
from models import Cat

def add_full_info():
    with app.app_context():
        # Полная дополнительная информация для всех 20 котов
        full_info = {
            "Барсик": {
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": False,
                "favorite_place": "Окно (любит наблюдать за птичками)",
                "vocal": "Разговорчивый (часто 'разговаривает' с хозяином)",
                "food_preferences": "Сухой корм премиум-класса, любит курицу",
                "adoption_recommendation": "Идеальный кот для активной семьи с детьми. Ему нужно много внимания и игр. Не рекомендуется заводить собаку, так как Барсик ревнив и может не поделить внимание. Лучше всего подойдёт для квартиры с большими окнами."
            },
            "Мурка": {
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Мягкий диван или кресло",
                "vocal": "Молчаливый (мяукает только когда хочет есть)",
                "food_preferences": "Гипоаллергенный корм, не переносит курицу",
                "adoption_recommendation": "Идеальный компаньон для пожилых людей или спокойной семьи. Ей нужно тихое место и правильное питание. Не требует активных игр, но ценит ласку и внимание."
            },
            "Рыжик": {
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Коробка (может часами играть с обычной коробкой)",
                "vocal": "Разговорчивый (любит 'петь' по утрам)",
                "food_preferences": "Влажный корм, любит рыбу",
                "adoption_recommendation": "Идеальный кот для семьи с детьми. Ему нужно много активных игр и внимания. Подойдёт для дома с другими животными. Рекомендуется стерилизация после выздоровления."
            },
            "Софи": {
                "kids_friendly": False,
                "cats_friendly": True,
                "dogs_friendly": False,
                "favorite_place": "Высокая лежанка у окна",
                "vocal": "Молчаливый (почти никогда не мяукает)",
                "food_preferences": "Сухой корм премиум-класс, любит рыбу",
                "adoption_recommendation": "Только для взрослых, без детей до 14 лет. Софи ищет спокойный дом и любящего хозяина. Она не требует много внимания, но ценит, когда с ней разговаривают и гладят."
            },
            "Тимофей": {
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Всюду, особенно любит высоту",
                "vocal": "Поющий (издаёт мелодичные звуки)",
                "food_preferences": "Всё ест, особенно любит мясо",
                "adoption_recommendation": "Идеальный кот для большой семьи с детьми. Ему нужно много пространства и внимания. Отлично ладит с другими животными. Нуждается в регулярном вычёсывании."
            },
            "Люся": {
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Под одеялом или на руках",
                "vocal": "Разговорчивый (любит 'беседовать')",
                "food_preferences": "Специальный корм для сфинксов",
                "adoption_recommendation": "Люся подойдёт для семьи, готовой к особому уходу. Нужно регулярное купание и увлажнение кожи. Очень ласковая, будет спать с вами под одеялом. Хорошо ладит с детьми и другими животными."
            },
            "Пушок": {
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": False,
                "favorite_place": "Тёплая лежанка у батареи",
                "vocal": "Молчаливый (мяукает только когда просит еду)",
                "food_preferences": "Лечебный корм для кошек с проблемами мочевыводящей системы",
                "adoption_recommendation": "Пушок ищет спокойный дом без собак и маленьких детей. Ему нужна диета и регулярное наблюдение у ветеринара. Идеальный компаньон для пожилых людей."
            },
            "Джесси": {
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Высота (верхние полки, шкафы)",
                "vocal": "Разговорчивый (любит 'рассказывать' о своих открытиях)",
                "food_preferences": "Сухой корм, любит рыбу",
                "adoption_recommendation": "Джесси уже нашла свой дом!"
            },
            "Маркиз": {
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Коробка (может часами сидеть в коробке)",
                "vocal": "Молчаливый (почти не мяукает)",
                "food_preferences": "Сухой корм премиум-класс",
                "adoption_recommendation": "Маркиз подойдёт для любой семьи. Он спокоен, не шалит, хорошо ладит с другими животными. Идеальный кот для квартиры."
            },
            "Боня": {
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "На руках у хозяина",
                "vocal": "Поющий (издаёт мелодичные звуки)",
                "food_preferences": "Молочная каша, влажный корм для котят",
                "adoption_recommendation": "Боня подойдёт для семьи с детьми. Она очень нежная и ласковая. Нуждается в вакцинации после выздоровления. Идеальна для первой кошки."
            },
            "Снежок": {
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": False,
                "favorite_place": "Окно (может часами смотреть на улицу)",
                "vocal": "Молчаливый (почти не мяукает)",
                "food_preferences": "Сухой корм, любит курицу",
                "adoption_recommendation": "Снежок подойдёт для спокойной семьи без собак. Ей нужен уютный дом и заботливый хозяин. Не переносит шум и громкие звуки."
            },
            "Шерхан": {
                "kids_friendly": True,
                "cats_friendly": False,
                "dogs_friendly": False,
                "favorite_place": "Везде (исследует каждый угол)",
                "vocal": "Разговорчивый (любит 'рассказывать' о своих приключениях)",
                "food_preferences": "Мясо, премиальный корм",
                "adoption_recommendation": "Шерхан подойдёт только для активных людей. Ему нужно много места для игр. Не рекомендуется для семей с другими животными — он хочет быть единственным. Отлично ладит с детьми."
            },
            "Карамелька": {
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Высота (верхние полки, шкафы)",
                "vocal": "Разговорчивый (любит 'беседовать')",
                "food_preferences": "Сухой корм, любит рыбу",
                "adoption_recommendation": "Карамелька подойдёт для активной семьи с детьми. Ей нужно много игрушек и пространства для игр. Рекомендуется стерилизация."
            },
            "Граф": {
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Диван (любит отдыхать в уюте)",
                "vocal": "Молчаливый (почти не мяукает)",
                "food_preferences": "Сухой корм премиум-класс",
                "adoption_recommendation": "Граф подойдёт для любой семьи. Он спокоен, не шалит, хорошо ладит с другими животными. Идеальный кот для квартиры."
            },
            "Зефирка": {
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Вода (может часами играть с водой)",
                "vocal": "Поющий (издаёт мелодичные звуки)",
                "food_preferences": "Влажный корм, любит рыбу",
                "adoption_recommendation": "Зефирка подойдёт для семьи с чувством юмора. Если вы готовы к её водным приключениям — она ваша! Очень ласковая и игривая. Хорошо ладит с детьми."
            },
            "Мартин": {
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Бегать (носится по квартире как ураган)",
                "vocal": "Разговорчивый (любит 'рассказывать')",
                "food_preferences": "Всё ест, особенно любит курицу",
                "adoption_recommendation": "Мартин подойдёт для активной семьи с детьми. Ему нужно много места для игр. Хорошо ладит с собаками. Рекомендуется стерилизация."
            },
            "Леди": {
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "На руках у хозяина",
                "vocal": "Молчаливый (почти не мяукает)",
                "food_preferences": "Сухой корм премиум-класс",
                "adoption_recommendation": "Леди уже нашла свой дом!"
            },
            "Тоша": {
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Спать (может спать часами)",
                "vocal": "Молчаливый (мяукает только когда просит еду)",
                "food_preferences": "Диетический корм для снижения веса",
                "adoption_recommendation": "Тоша подойдёт для спокойной семьи. Ему нужна диета и регулярные прогулки для снижения веса. Не требует активных игр, любит отдыхать."
            },
            "Симба": {
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Игры (обожает активные развлечения)",
                "vocal": "Поющий (издаёт мелодичные звуки)",
                "food_preferences": "Мясо, премиальный корм",
                "adoption_recommendation": "Симба подойдёт для большой семьи с детьми. Ему нужно много места для игр. Хорошо ладит с другими животными. Нуждается в регулярном вычёсывании."
            },
            "Жозефина": {
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Под одеялом (обожает тепло)",
                "vocal": "Разговорчивый (любит 'беседовать')",
                "food_preferences": "Специальный корм для сфинксов",
                "adoption_recommendation": "Жозефина подойдёт для семьи, готовой к особому уходу. Нужно регулярное купание и увлажнение кожи. Очень ласковая, будет спать с вами под одеялом. Хорошо ладит с детьми и другими животными."
            }
        }
        
        updated = 0
        for name, info in full_info.items():
            cat = Cat.query.filter_by(name=name).first()
            if cat:
                cat.kids_friendly = info["kids_friendly"]
                cat.cats_friendly = info["cats_friendly"]
                cat.dogs_friendly = info["dogs_friendly"]
                cat.favorite_place = info["favorite_place"]
                cat.vocal = info["vocal"]
                cat.food_preferences = info["food_preferences"]
                cat.adoption_recommendation = info["adoption_recommendation"]
                updated += 1
                print(f"✅ Обновлён: {name}")
            else:
                print(f"⚠️ Не найден: {name}")
        
        db.session.commit()
        print(f"\n✅ Добавлена полная информация для {updated} котиков!")

if __name__ == "__main__":
    add_full_info()