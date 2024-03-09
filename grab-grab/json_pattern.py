def into_json(org_id, company_id, name, city, address, website, ypage, rating, phones, categories, reviews, goods, opening_hours):
    """ Шаблон файла OUTPUT.json"""

    data_grabbed = {
        "ID": org_id,
        "company_id": company_id,
        "name": name,
        "city": city,
        "address": address,
        "website": website,
        "ypage": ypage,
        "rating": rating,
        "categories": categories,
        "reviews": reviews,
        "goods": goods,
        "opening_hours":{},
        "phones": phones

    }

    if opening_hours:
        opening_hours_new = []
        days = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']

        # Проверка opening_hours на отсутствие одного из рабочих дней
        # Создается отдельный список (opening_hours_new) с полученными значениями
        # Далее он проверяется на отсутствие того или иного рабочего дня
        # На индекс отсутствующего элемента вставляется значение  "   выходной"
        for day in opening_hours:
            opening_hours_new.append(day[:2].lower())
        for i in days:
            if i not in opening_hours_new:
                opening_hours.insert(days.index(i), '   выходной')
        data_grabbed['opening_hours'] = {
            "mon": opening_hours[0][3:],
            "tue": opening_hours[1][3:],
            "wed": opening_hours[2][3:],
            "thu": opening_hours[3][3:],
            "fri": opening_hours[4][3:],
            "sat": opening_hours[5][3:],
            "sun": opening_hours[6][3:]
        }

    return data_grabbed
