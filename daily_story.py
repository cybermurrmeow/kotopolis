from __future__ import annotations

import fcntl
import json
import os
import re

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from flask import request, url_for

from models import Cat
from story_bank import STORY_BANK


MOSCOW_TZ = ZoneInfo(
    "Europe/Moscow"
)

ADOPTED_STATUS = (
    "Усыновлён"
)


def clean(value):
    if value is None:
        return ""

    value = str(
        value
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


def shorten(
    value,
    limit=480
):
    value = clean(
        value
    )

    if (
        len(value)
        <=
        limit
    ):
        return value

    part = value[:limit]

    sentence = max(
        part.rfind("."),
        part.rfind("!"),
        part.rfind("?")
    )

    if (
        sentence
        >
        limit // 2
    ):
        return (
            part[
                :sentence + 1
            ]
        )

    space = part.rfind(
        " "
    )

    if space > 0:
        part = part[:space]

    return (
        part.rstrip(
            " ,;:-"
        )
        +
        "…"
    )


def available_cats():

    return (
        Cat.query
        .filter(
            Cat.status
            !=
            ADOPTED_STATUS
        )
        .order_by(
            Cat.id.asc()
        )
        .all()
    )


def cat_facts(cat):

    facts = []


    def add(
        label,
        value
    ):

        value = clean(
            value
        )

        if value:

            facts.append(
                (
                    label,
                    value
                )
            )


    add(
        "порода",
        getattr(
            cat,
            "breed",
            None
        )
    )

    add(
        "характер",
        getattr(
            cat,
            "personality",
            None
        )
    )

    add(
        "настроение",
        getattr(
            cat,
            "mood",
            None
        )
    )

    add(
        "активность",
        getattr(
            cat,
            "activity_level",
            None
        )
    )

    add(
        "любимая игрушка",
        getattr(
            cat,
            "favorite_toy",
            None
        )
    )

    add(
        "любимое место",
        getattr(
            cat,
            "favorite_place",
            None
        )
    )

    add(
        "предпочтения в еде",
        getattr(
            cat,
            "food_preferences",
            None
        )
    )


    vocal = getattr(
        cat,
        "vocal",
        None
    )

    if vocal is True:

        facts.append(
            (
                "разговорчивость",
                "любит общаться голосом"
            )
        )

    elif vocal is False:

        facts.append(
            (
                "разговорчивость",
                "обычно ведёт себя тихо"
            )
        )


    compatibility = [
        (
            "с детьми",
            getattr(
                cat,
                "kids_friendly",
                None
            )
        ),
        (
            "с кошками",
            getattr(
                cat,
                "cats_friendly",
                None
            )
        ),
        (
            "с собаками",
            getattr(
                cat,
                "dogs_friendly",
                None
            )
        )
    ]


    for label, value in compatibility:

        if value is True:

            facts.append(
                (
                    label,
                    "дружелюбен"
                )
            )

        elif value is False:

            facts.append(
                (
                    label,
                    "лучше знакомить осторожно"
                )
            )


    return facts


def narrative_values(cat):

    values = []


    for field in [
        "story",
        "description",
        "adoption_recommendation"
    ]:

        value = clean(
            getattr(
                cat,
                field,
                None
            )
        )

        if (
            value
            and
            value not in values
        ):

            values.append(
                value
            )


    return values


def _contains(value, *words):
    value = clean(value).lower()

    return any(
        word.lower() in value
        for word in words
    )


def _gender_words(cat):
    gender = clean(
        getattr(
            cat,
            "gender",
            ""
        )
    ).lower()

    female = (
        "дев" in gender
        or
        "жен" in gender
        or
        "кошк" in gender
    )

    if female:
        return {
            "he": "она",
            "him": "ней",
            "ready": "готова",
            "curious": "любопытная",
            "calm": "спокойная",
        }

    return {
        "he": "он",
        "him": "нём",
        "ready": "готов",
        "curious": "любопытный",
        "calm": "спокойный",
    }


def _story_signals(cat):
    return {
        "personality":
            clean(
                getattr(
                    cat,
                    "personality",
                    ""
                )
            ),

        "activity":
            clean(
                getattr(
                    cat,
                    "activity_level",
                    ""
                )
            ),

        "mood":
            clean(
                getattr(
                    cat,
                    "mood",
                    ""
                )
            ),

        "toy":
            clean(
                getattr(
                    cat,
                    "favorite_toy",
                    ""
                )
            ),

        "place":
            clean(
                getattr(
                    cat,
                    "favorite_place",
                    ""
                )
            ),

        "food":
            clean(
                getattr(
                    cat,
                    "food_preferences",
                    ""
                )
            ),

        "story":
            clean(
                getattr(
                    cat,
                    "story",
                    ""
                )
            ),

        "description":
            clean(
                getattr(
                    cat,
                    "description",
                    ""
                )
            ),

        "recommendation":
            clean(
                getattr(
                    cat,
                    "adoption_recommendation",
                    ""
                )
            ),

        "kids":
            getattr(
                cat,
                "kids_friendly",
                None
            ),

        "cats":
            getattr(
                cat,
                "cats_friendly",
                None
            ),

        "dogs":
            getattr(
                cat,
                "dogs_friendly",
                None
            ),

        "vocal":
            getattr(
                cat,
                "vocal",
                None
            ),
    }


def _personality_scene(
    cat,
    data
):
    name = clean(cat.name)

    value = (
        data["personality"]
        +
        " "
        +
        data["mood"]
    )

    if _contains(
        value,
        "открыт",
        "дружелюб",
        "общитель",
        "ласков"
    ):
        return (
            f"{name} производит впечатление котика, "
            "который не хочет проживать жизнь в стороне от людей. "
            "Ему интересно быть рядом, замечать происходящее и становиться "
            "частью обычных домашних дел. Похоже, для полного счастья ему "
            "не хватает только собственного человека."
        )

    if _contains(
        value,
        "спокой",
        "тих",
        "нежн"
    ):
        return (
            f"У {name} совсем не тот характер, который требует постоянного "
            "внимания. Рядом с ним скорее хочется немного замедлиться. "
            "Такой котик может просто находиться неподалёку и своим "
            "присутствием делать пространство уютнее."
        )

    if _contains(
        value,
        "игрив",
        "весёл",
        "озор",
        "актив"
    ):
        return (
            f"С {name} трудно представить совсем скучный день. "
            "Кажется, вокруг него всегда найдётся что изучить, проверить "
            "или превратить в маленькое приключение. Даже обычный вечер "
            "дома с таким соседом наверняка будет немного живее."
        )

    if _contains(
        value,
        "осторож",
        "скром",
        "застен",
        "независ"
    ):
        return (
            f"{name} не из тех, кто раскрывается перед каждым сразу. "
            "Ему важнее сначала присмотреться и понять, что рядом безопасно. "
            "Зато доверие такого котика ощущается особенно ценным, потому "
            "что появляется не случайно."
        )

    return (
        f"У {name} свой характер и свой способ знакомиться с миром. "
        "За короткой анкетой всегда скрывается гораздо больше, чем можно "
        "уместить в несколько характеристик. Именно поэтому иногда лучше "
        "просто познакомиться поближе."
    )


def _activity_scene(
    cat,
    data
):
    name = clean(cat.name)

    value = (
        data["activity"]
        +
        " "
        +
        data["personality"]
    )

    if _contains(
        value,
        "высок",
        "актив",
        "энергич",
        "игрив"
    ):
        return (
            f"Если бы {name} самостоятельно составлял распорядок дня, "
            "в нём наверняка нашлось бы место для исследования квартиры, "
            "игры и ещё одного небольшого приключения. Такой характер "
            "особенно хорошо раскрывается там, где котику дают возможность "
            "двигаться, интересоваться и быть собой."
        )

    if _contains(
        value,
        "низк",
        "спокой",
        "умерен"
    ):
        return (
            f"Для {name} хороший день совсем не обязан быть насыщенным. "
            "Иногда достаточно спокойного места, знакомых звуков и человека "
            "рядом. В такой простой домашней жизни как раз и может оказаться "
            "то самое ощущение безопасности, которого ждёт котик."
        )

    return (
        f"У каждого котика свой ритм, и {name} не исключение. "
        "Кому-то нужны бесконечные игры, кому-то спокойное наблюдение за "
        "происходящим. Главное, чтобы рядом оказался человек, который "
        "заметит этот ритм и не станет его ломать."
    )


def _home_scene(
    cat,
    data
):
    name = clean(cat.name)

    if data["place"]:
        return (
            f"У {name} уже есть свои маленькие привычки и любимые уголки. "
            "Именно из таких мелочей постепенно появляется чувство дома: "
            "знакомое место, спокойная обстановка и уверенность, что завтра "
            "никуда не придётся уходить. Возможно, следующий любимый уголок "
            f"{name} найдёт уже в собственной семье."
        )

    return (
        f"Для {name} дом пока существует скорее как возможность, чем как "
        "привычное место. Но котикам не нужны сложные вещи. Постоянство, "
        "безопасность и человек, которого начинаешь узнавать день за днём, "
        "иногда значат намного больше всего остального."
    )


def _trust_scene(
    cat,
    data
):
    name = clean(cat.name)

    friendly_count = sum(
        value is True
        for value in [
            data["kids"],
            data["cats"],
            data["dogs"],
        ]
    )

    if friendly_count >= 2:
        return (
            f"Похоже, {name} умеет принимать окружающих без лишней драмы. "
            "Для будущего дома это хорошая основа: знакомство можно строить "
            "спокойно, постепенно превращая новых соседей в привычную часть "
            "жизни. Самое важное здесь не спешить и дать отношениям сложиться."
        )

    if friendly_count == 1:
        return (
            f"{name} уже показывает, что способен находить общий язык с "
            "окружающими. Но настоящий дом всё равно начинается не с галочки "
            "в анкете, а с нормального знакомства. Немного времени и уважения "
            "к границам могут рассказать о котике гораздо больше."
        )

    return (
        f"Про отношения {name} с будущими домашними пока нельзя рассказать "
        "одной короткой фразой. И это нормально. У котиков, как и у людей, "
        "доверие появляется постепенно. Хорошее знакомство всегда начинается "
        "с возможности не торопиться."
    )


def _voice_scene(
    cat,
    data
):
    name = clean(cat.name)

    if data["vocal"] is True:
        return (
            f"С {name}, похоже, можно не только жить рядом, но и вести "
            "настоящие разговоры. Некоторые котики отлично умеют напоминать "
            "о себе голосом, встречать человека и комментировать происходящее. "
            "В доме с таким жильцом тишина точно перестаёт быть абсолютной."
        )

    if data["vocal"] is False:
        return (
            f"{name} скорее относится к тем котикам, которым не обязательно "
            "постоянно заявлять о себе. Иногда достаточно взгляда, движения "
            "или тихого присутствия рядом, чтобы всё было понятно без слов."
        )

    return (
        f"Пока неизвестно, насколько разговорчивым окажется {name} дома. "
        "Такие привычки часто проявляются только тогда, когда котик полностью "
        "осваивается и понимает, что рядом безопасно."
    )


def _past_scene(
    cat,
    data
):
    name = clean(cat.name)

    source = (
        data["story"]
        or
        data["description"]
    )

    if not source:
        return (
            f"У {name} ещё будет история, которую нельзя прочитать в старой "
            "анкете. Она начнётся уже после приюта: с нового дома, знакомых "
            "шагов за дверью и места, куда можно возвращаться каждый день."
        )

    if _contains(
        source,
        "улиц",
        "нашли",
        "двор",
        "гараж",
        "подобрал"
    ):
        return (
            f"В жизни {name} уже был период, когда привычного дома рядом не "
            "оказалось. Теперь самое интересное может быть впереди. Не поиск "
            "следующего временного места, а совершенно обычная домашняя жизнь, "
            "в которой не нужно каждый раз начинать всё заново."
        )

    return (
        f"У {name} уже есть прошлое, которое привело его в Котополис. "
        "Но приют не обязан становиться главным событием всей жизни котика. "
        "Гораздо приятнее думать, что самая важная её часть ещё даже "
        "не началась."
    )


def _future_scene(
    cat,
    data
):
    name = clean(cat.name)

    if data["recommendation"]:
        return (
            f"Когда смотришь на {name}, интереснее думать не о том, как "
            "выглядит его анкета сейчас, а о том, каким станет обычный день "
            "после усыновления. Своя миска, знакомая комната, человек, чьи "
            "шаги уже узнаёшь. Именно такие маленькие вещи постепенно "
            "становятся новой жизнью."
        )

    return (
        f"Возможно, главное событие для {name} ещё впереди. "
        "Не что-то большое и громкое, а первый день, когда новое место "
        "перестанет быть незнакомым. Потом появятся привычки, любимые точки "
        "в квартире и человек, возвращения которого действительно ждёшь."
    )


def build_story(
    cat,
    variant
):
    stories = STORY_BANK.get(
        cat.id
    )

    if stories:

        story = stories[
            variant
            %
            len(stories)
        ]

        story = (
            story
            .replace("—", "-")
            .replace("–", "-")
            .strip()
        )

        return {
            "text": story,
            "chips": []
        }


    # --------------------------------------------------
    # Fallback only for future cats that are not yet
    # present in the manually written story bank.
    # --------------------------------------------------

    name = clean(
        getattr(
            cat,
            "name",
            "Котик"
        )
    )

    personality = clean(
        getattr(
            cat,
            "personality",
            ""
        )
    )

    description = clean(
        getattr(
            cat,
            "description",
            ""
        )
    )

    story_source = clean(
        getattr(
            cat,
            "story",
            ""
        )
    )

    activity = clean(
        getattr(
            cat,
            "activity_level",
            ""
        )
    )


    variants = []


    if personality:

        variants.append(
            f"{name} постепенно показывает свой характер в обычных мелочах. "
            f"Сейчас его лучше всего описывает фраза: {personality.lower()}. "
            "Но настоящее знакомство всегда оказывается интереснее любой короткой характеристики."
        )


    if description:

        variants.append(
            f"За привычками {name} интересно наблюдать день за днём. "
            "В приюте постепенно становится понятно, какие вещи помогают ему "
            "чувствовать себя спокойнее и увереннее. "
            "Следующая важная привычка должна появиться уже в собственном доме."
        )


    if story_source:

        variants.append(
            f"У {name} уже есть прошлое, которое привело его в Котополис. "
            "Но гораздо важнее то, что эта история ещё совсем не закончена. "
            "Самая домашняя её часть всё ещё впереди."
        )


    if activity:

        variants.append(
            f"У {name} есть собственный ритм жизни, и именно к нему лучше прислушиваться. "
            "Хороший дом не пытается переделать кота под себя, а постепенно находит "
            "удобный темп для всех."
        )


    variants.append(
        f"Сегодня в центре внимания {name}. "
        "Иногда котику не нужна сложная история, чтобы стать для кого-то особенным. "
        "Достаточно одного удачного знакомства, после которого временное место "
        "превращается в прошлое."
    )


    story = variants[
        variant
        %
        len(variants)
    ]


    story = (
        story
        .replace("—", "-")
        .replace("–", "-")
        .strip()
    )


    return {
        "text": story,
        "chips": []
    }


def state_paths(app):

    directory = (
        Path(
            app.root_path
        )
        /
        "data"
    )

    directory.mkdir(
        parents=True,
        exist_ok=True
    )

    return (
        directory
        /
        "daily_story_state.json",

        directory
        /
        "daily_story_state.lock"
    )


def read_state(path):

    if not path.exists():
        return {}

    try:

        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        if isinstance(
            data,
            dict
        ):
            return data

    except Exception:
        pass

    return {}


def write_state(
    path,
    state
):

    temp = Path(
        str(path)
        +
        ".tmp"
    )

    temp.write_text(
        json.dumps(
            state,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    os.replace(
        temp,
        path
    )


def choose_story(
    app
):

    cats = available_cats()


    if not cats:
        return None


    by_id = {
        cat.id:
            cat
        for cat
        in cats
    }


    state_path, lock_path = (
        state_paths(
            app
        )
    )


    today = (
        datetime.now(
            MOSCOW_TZ
        )
        .date()
        .isoformat()
    )


    with lock_path.open(
        "a+",
        encoding="utf-8"
    ) as lock:

        fcntl.flock(
            lock.fileno(),
            fcntl.LOCK_EX
        )


        state = read_state(
            state_path
        )


        current_id = (
            state.get(
                "cat_id"
            )
        )


        # Если кот всё ещё существует,
        # не усыновлён и день тот же,
        # история остаётся стабильной.
        if (
            state.get(
                "date"
            )
            ==
            today
            and
            current_id
            in by_id
            and
            state.get(
                "text"
            )
        ):

            cat = by_id[
                current_id
            ]

            return format_result(
                cat,
                state.get(
                    "text",
                    ""
                ),
                state.get(
                    "chips",
                    []
                )
            )


        eligible_ids = set(
            by_id.keys()
        )


        shown = []

        for value in state.get(
            "cycle_shown",
            []
        ):

            try:

                value = int(
                    value
                )

            except Exception:
                continue


            if (
                value
                in eligible_ids
            ):

                shown.append(
                    value
                )


        remaining = [
            cat
            for cat
            in cats
            if cat.id
            not in shown
        ]


        # Все котики уже прошли круг.
        # Начинаем следующий круг.
        if not remaining:

            shown = []

            remaining = list(
                cats
            )


        # Детерминированный выбор,
        # чтобы два gunicorn worker
        # не выбирали разных котов.
        day_number = (
            datetime.now(
                MOSCOW_TZ
            )
            .date()
            .toordinal()
        )


        index = (
            day_number
            %
            len(remaining)
        )


        cat = remaining[
            index
        ]


        variants = (
            state.get(
                "variants",
                {}
            )
        )


        try:

            variant = int(
                variants.get(
                    str(
                        cat.id
                    ),
                    0
                )
            )

        except Exception:

            variant = 0


        story = build_story(
            cat,
            variant
        )


        variants[
            str(
                cat.id
            )
        ] = (
            variant
            +
            1
        )


        shown.append(
            cat.id
        )


        new_state = {
            "date":
                today,

            "cat_id":
                cat.id,

            "cycle_shown":
                shown,

            "variants":
                variants,

            "text":
                story[
                    "text"
                ],

            "chips":
                story[
                    "chips"
                ]
        }


        write_state(
            state_path,
            new_state
        )


        return format_result(
            cat,
            story[
                "text"
            ],
            story[
                "chips"
            ]
        )


def format_result(
    cat,
    text,
    chips
):

    photo_path = clean(
        getattr(
            cat,
            "photo_path",
            None
        )
    )


    if photo_path:

        if (
            photo_path.startswith(
                "http://"
            )
            or
            photo_path.startswith(
                "https://"
            )
        ):

            photo_url = (
                photo_path
            )

        else:

            photo_url = url_for(
                "static",
                filename=
                    photo_path
            )

    else:

        photo_url = None


    return {
        "cat":
            cat,

        "text":
            text,

        "chips":
            chips,

        "photo_url":
            photo_url
    }


def register_daily_story(
    app
):

    @app.context_processor
    def inject_daily_story():

        if (
            request.endpoint
            !=
            "dashboard"
        ):

            return {}


        return {
            "daily_story":
                choose_story(
                    app
                )
        }
