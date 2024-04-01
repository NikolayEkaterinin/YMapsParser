<!-- Title -->
<h1 align="center">YMapsParser</h1>

---

> Парсер для Яндекс.Карт, собирающий информацию об организациях в выбранной области поиска  
> 
> Это доработанная версия https://github.com/chernyshov-dp/YMapsGrabber
---

## Стек
- Python 3.9
- Selenium + safaridriver
- beautifulsoup4 + lxml
- json

## Список собираемой информации с Яндекс.Карт
- Название организации
- Id организации
- Город
- Адрес
- Сайт организации
- Часы работы (по дням недели)
- Ссылка на карточку организации
- Меню/услуги
- Рейтинг
- Отзывы
- Номера телефонов

## Установка и запуск
```console
git clone git@github.com:redrum0x/YMapsParser.git
cd YMapsParser/grab-grab
pip3 install -r requirements.txt
python3 main.py --cities="москва" --search=банк --count=100 --output="../out/file.json"
```

Некоторые поля являются опциональными и по умолчанию не парсятся, их можно добавить, указав 
```console
--columns=reviews,categories,goods,opening_hours,phones
````

Файл со списком городов
```console
--cities_file="../dist/cities.txt" 
````

Список городов
```console
--cities="Москва,Ростов" 
````

Поисковая фраза
```console
--search="Кафе" 
````

Файл со списком поисковых фраз
```console
--search_file="../dist/cities.txt" 
````

Браузер (safari, chrome)
```console
--driver="safari" 
````

Количество компаний
```console
--count=2000 
````

Файл с результатами
```console
--output="../out/file.json"
````


## Лицензия
[GNU General Public License v3.0](https://github.com/redrum0x/YMapsParser/blob/main/LICENSE)
