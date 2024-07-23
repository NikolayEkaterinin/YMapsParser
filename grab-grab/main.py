from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime, timezone

import chromedriver_binary  # Добавляет chromedriver в путь

import traceback
import argparse
import sys
import json
import json_pattern
import util_module
from infogetter import InfoGetter


class GrabberApp:
    def __init__(self, cities, search, count, output_file, columns, driver_name):
        self.cities = cities
        self.search = search
        self.output_file = output_file
        self.count = count
        self.columns = columns
        self.driver_name = driver_name

    def decode_data(self, data):
        """Функция декодирования данных перед сохранением в JSON файл."""
        decoded_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                decoded_data[key] = value.encode(
                    'utf-8', errors='ignore').decode('utf-8')
            elif isinstance(value, list):
                decoded_data[key] = [v.encode(
                    'utf-8', errors='ignore').decode('utf-8') if isinstance(v, str) else v for v in value]
            elif isinstance(value, dict):
                decoded_data[key] = self.decode_data(value)
            else:
                decoded_data[key] = value
        return decoded_data

    def grab_data(self):
        open(self.output_file, "w").close()

        # Выбор драйвера
        if self.driver_name == "chrome":
            chrome_options = Options()
            chrome_options.add_argument("--disable-extensions")

            driver = webdriver.Chrome(service=Service(
                ChromeDriverManager().install()), options=chrome_options)

        elif self.driver_name == "safari":
            driver = webdriver.Safari()

        driver.maximize_window()

        for city in self.cities:
            city = city.strip().lower()

            if not city:
                raise ValueError("City is empty")

            for search in self.search:
                search = search.strip()

                if not search:
                    print(datetime.now(timezone.utc).strftime(
                        '%F %T.%f')[:-3]+". Search is empty")
                    continue

                driver.get(
                    "https://yandex.ru/maps/1/a/search/"
                    + city
                    + ", "
                    + search
                    + "/"
                )

                sleep(0.8)
                InfoGetter.check_captcha(driver)

                soup = BeautifulSoup(driver.page_source, "lxml")

                print(datetime.now(timezone.utc).strftime('%F %T.%f')[
                      :-3]+". Start parse city " + city + ". Search " + search+". Url "+driver.current_url)

                items_in_page = 0
                old_items_in_page = 0
                cityErrors = 0

                try:
                    for i in range(int(self.count)):

                        try:
                            if (i + 4) > old_items_in_page:
                                items_in_page = driver.execute_script(
                                    "document.getElementsByClassName('search-business-snippet-view')[document.getElementsByClassName('search-business-snippet-view').length -1].scrollIntoView();return document.getElementsByClassName('search-business-snippet-view').length;"
                                )
                                sleep(0.2)

                                if old_items_in_page == items_in_page:
                                    soup = BeautifulSoup(
                                        driver.page_source, "lxml")
                                    if not soup.body.findAll(text='если не нашли их на карте'):
                                        print(datetime.now(timezone.utc).strftime('%F %T.%f')[
                                              :-3]+". old_items_in_page == items_in_page. Load finish")
                                    else:
                                        print(datetime.now(timezone.utc).strftime('%F %T.%f')[
                                              :-3]+". old_items_in_page == items_in_page. sleep 2")
                                        sleep(2)

                                old_items_in_page = items_in_page

                                print(datetime.now(timezone.utc).strftime('%F %T.%f')[
                                      :-3]+". Items in page " + str(items_in_page))
                        except Exception as e:
                            print(traceback.format_exc())
                            sleep(1)

                        try:
                            driver.execute_script(
                                "document.getElementsByClassName('search-business-snippet-view')[" + str(
                                    i) + "].click();"
                            )
                        except Exception as e:
                            print(traceback.format_exc())
                            print("---------------------------")
                            print("---------------------------")
                            print("---------------------------")
                            break

                        sleep(0.2)

                        soup = BeautifulSoup(driver.page_source, "lxml")

                        InfoGetter.check_captcha(driver)

                        ypage = InfoGetter.get_company_url(soup)

                        print(datetime.now(timezone.utc).strftime('%F %T.%f')[
                              :-3]+". "+str(i) + ". "+city+". Get company " + ypage)

                        name = InfoGetter.get_name(soup)
                        address = InfoGetter.get_address(soup)
                        website = InfoGetter.get_website(soup)
                        company_id = InfoGetter.get_company_id(soup)
                        rating = InfoGetter.get_rating(soup)

                        if city not in address.lower():
                            cityErrors += 1
                            print(datetime.now(timezone.utc).strftime('%F %T.%f')[
                                  :-3]+". -- " + city+". Invalid city in address "+address+". Errors count "+str(cityErrors))
                            print("---------------------------")
                            print("---------------------------")
                            print("---------------------------")

                            if cityErrors < 3:
                                print("continue")
                                continue
                            break

                        cityErrors = 0

                        phones = []
                        if "phones" in self.columns:
                            print(datetime.now(timezone.utc).strftime(
                                '%F %T.%f')[:-3]+". -- Get phones")
                            phones = InfoGetter.get_search_phones(
                                soup, driver, i)

                        print(datetime.now(timezone.utc).strftime('%F %T.%f')
                              [:-3]+". -- Phones " + str(phones))

                        opening_hours = []
                        if "opening_hours" in self.columns:
                            print(datetime.now(timezone.utc).strftime('%F %T.%f')
                                  [:-3]+". -- Get opening hours")
                            opening_hours = InfoGetter.get_opening_hours(soup)

                        categories = []
                        if "categories" in self.columns:
                            print(datetime.now(timezone.utc).strftime(
                                '%F %T.%f')[:-3]+". -- Get categories")
                            categories = InfoGetter.get_categories(
                                soup, driver)

                        goods = []
                        if "goods" in self.columns:
                            print(datetime.now(timezone.utc).strftime(
                                '%F %T.%f')[:-3]+". -- Get goods")
                            try:
                                menu = driver.find_element(
                                    By.CLASS_NAME, "card-feature-view__main-content")
                                menu_text = driver.find_element(
                                    By.CLASS_NAME, "card-feature-view__main-content").text

                                if ("товары и услуги" in menu_text.lower()) or (
                                    "меню" in menu_text.lower()
                                ):
                                    # Нажимаем на кнопку "Меню"/"Товары и услуги"
                                    menu.click()
                                    sleep(2)
                                    soup = BeautifulSoup(
                                        driver.page_source, "lxml")
                                    goods = InfoGetter.get_goods(soup)
                            except NoSuchElementException:
                                pass

                        reviews = []
                        if "reviews" in self.columns:
                            reviews = InfoGetter.get_reviews(soup, driver)

                        if company_id:
                            # Записываем данные в OUTPUT.json
                            data = {
                                "company_id": company_id,
                                "name": name,
                                "city": city.strip().title(),
                                "address": address,
                                "website": website,
                                "ypage": ypage,
                                "rating": rating,
                                "phones": phones,
                                "categories": categories,
                                "reviews": reviews,
                                "goods": goods,
                                "opening_hours": opening_hours,
                            }

                            decoded_data = self.decode_data(data)
                            with open(self.output_file, "a", encoding='utf-8') as file:
                                file.write(json.dumps(
                                    decoded_data, ensure_ascii=False, indent=4))
                                file.write("\n")
                            print(datetime.now(timezone.utc).strftime('%F %T.%f')[
                                  :-3]+". -- Added " + name + ". " + ypage)

                except Exception as e:
                    print(traceback.format_exc())
                    pass

                print(datetime.now(timezone.utc).strftime('%F %T.%f')
                      [:-3]+". Saved to " + self.output_file)
        driver.quit()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--cities", help="Список городов")
    parser.add_argument("--cities_file", help="Файл со списком городов")
    parser.add_argument("--search", help="Поисковая фраза")
    parser.add_argument("--search_file", help="Файл со списком поисковых фраз")
    parser.add_argument("--output", help="Файл для вывода данных")
    parser.add_argument("--count", help="Количество компаний")
    parser.add_argument("--driver", help="Имя браузера (chrome, safari)")
    parser.add_argument(
        "--columns",
        help="Опциональные колонки: reviews, categories, goods, opening_hours, phones",
    )

    args = parser.parse_args()

    cities = []
    search = []

    driver = "safari"
    if args.driver:
        if args.driver in ["chrome", "safari"]:
            driver = args.driver
        else:
            raise ValueError("Неверное значение для параметра driver")

    columns = args.columns.split(",") if args.columns else []

    output = "../out/" + (args.search if args.search else "output") + ".json"

    if args.cities:
        cities = args.cities.split(",")

    if args.cities_file:
        with open(args.cities_file, encoding='utf-8') as f:
            cities = f.readlines()

    if not cities:
        raise ValueError("Список городов пуст")

    if args.search:
        search.append(args.search)

    if args.search_file:
        with open(args.search_file, encoding='utf-8') as f:
            search = f.readlines()

    if not search:
        raise ValueError("Список поисковых фраз пуст")

    grabber = GrabberApp(cities, search, args.count, output, columns, driver)
    grabber.grab_data()


if __name__ == "__main__":
    main()
