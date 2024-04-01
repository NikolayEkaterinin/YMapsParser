from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException, MoveTargetOutOfBoundsException
from selenium.webdriver import ActionChains
from time import sleep
from datetime import datetime
from pygame import mixer
import json

class InfoGetter(object):
    """ Класс с логикой парсинга данных из объекта BeautifulSoup"""

    @staticmethod
    def get_name(soup_content):
        """ Получение названия организации """

        try:
            for data in soup_content.find_all("h1", {"class": "card-title-view__title"}):
                name = data.getText()

            return name
        except Exception:
            return ""

    @staticmethod
    def check_captcha(driver):
        """ Проверка капчи """
        soup = BeautifulSoup(driver.page_source, "lxml")
        print(datetime.utcnow().strftime('%F %T.%f')[:-3]+". Check")
        if soup.find_all("div", {"class": "CheckboxCaptcha"}) or soup.find_all("div", {"class": "AdvancedCaptcha"}) :
            print(datetime.utcnow().strftime('%F %T.%f')[:-3]+". Captcha. Wait 20s")
            mixer.init()
            mixer.music.load('../dist/alert.wav')
            mixer.music.play()
            sleep(20)
            InfoGetter.check_captcha(driver)


    @staticmethod
    def get_address(soup_content):
        """ Получение адреса организации """

        try:
            for data in soup_content.find_all("div", {"class": "business-contacts-view__address-link"}):
                address = data.getText()

            return address
        except Exception:
            return ""

    @staticmethod
    def get_company_url(soup_content):
        """ Получение url"""

        try:
            for data in soup_content.find_all("a", {"class": "card-title-view__title-link"}):
                url = "https://yandex.ru"+data.get('href')

            return url
        except Exception as e:
            print('get_company_url error '+getattr(e, 'message', repr(e)))
            return ""

    @staticmethod
    def get_company_id(soup_content):
        """ Получение id"""

        try:
            for data in soup_content.find_all("div", {"class": "business-card-view"}):
                website = data.get('data-id')

            return website
        except Exception as e:
            print('get_company_id error '+getattr(e, 'message', repr(e)))
            return ""

    @staticmethod
    def get_website(soup_content):
        """ Получение сайта организации"""

        try:
            for data in soup_content.find_all("span", {"class": "business-urls-view__text"}):
                website = data.getText()

            return website
        except Exception:
            return ""

    @staticmethod
    def get_opening_hours(soup_content):
        """ Получение графика работы"""

        opening_hours = []
        try:
            for data in soup_content.find_all("meta", {"itemprop": "openingHours"}):
                opening_hours.append(data.get('content'))

            return opening_hours
        except Exception as e:
            print('get_categories error '+getattr(e, 'message', repr(e)))
            return ""

    @staticmethod
    def get_goods(soup_content):
        """ Получение списка товаров и услуг"""

        dishes = []
        prices = []

        try:
            # Получаем название блюда/товара/услуги (из меню-витрины)
            for dish_s in soup_content.find_all("div", {"class": "related-item-photo-view__title"}):
                dishes.append(dish_s.getText())

            # Получаем цену блюда/товара/услуги (из меню-витрины)
            for price_s in soup_content.find_all("span", {"class": "related-product-view__price"}):
                prices.append(price_s.getText())

            # Получаем название блюда/товара/услуги (из меню-списка)
            for dish_l in soup_content.find_all("div", {"class": "related-item-list-view__title"}):
                dishes.append(dish_l.getText())

            # Получаем цену блюда/товара/услуги (из меню-списка)
            for price_l in soup_content.find_all("div", {"class": "related-item-list-view__price"}):
                prices.append(price_l.getText())

        # Если меню организации полностью представлено в виде списка
        except NoSuchElementException:
            try:
                # Получаем название блюда/товара/услуги (из меню-списка)
                for dish_l in soup_content.find_all("div", {"class": "related-item-list-view__title"}):
                    dishes.append(dish_l.getText())

                # Получаем цену блюда/товара/услуги (из меню-списка)
                for price_l in soup_content.find_all("div", {"class": "related-item-list-view__price"}):
                    prices.append(price_l.getText())
            except Exception:
                pass

        except Exception:
            return ""

        return dict(zip(dishes, prices))

    @staticmethod
    def get_search_phones(soup_content, driver, i):
        """ Получение номеров из карточки на странице поиска"""
        phones = []

        try:
            driver.execute_script("document.getElementsByClassName('card-phones-view__more')[0].click();")
#            sleep(0.2)

            driver.execute_script("document.getElementsByClassName('card-phones-view__phone-number')[0].click();")
#            sleep(0.2)

            soup_content = BeautifulSoup(driver.page_source, "lxml")

            for data in soup_content.find_all("div", {"class": "card-phones-view__phone-number"}):
                phones.append(data.getText())

            phones = list(set(phones))
            return phones
        except Exception as e:
            err = getattr(e, 'message', repr(e))
            if "undefined is not an object" in err:
                return []
            print('get_phones error '+err)
            return []


    @staticmethod
    def get_categories(soup_content, driver):
        """ Получение категорий"""
        categories = []

        try:
            for data in soup_content.find_all("a", {"class": "business-categories-view__category"}):
                categories.append(data.getText())

            categories = list(set(categories))
            return categories
        except Exception as e:
            print('get_categories error '+getattr(e, 'message', repr(e)))
            return ""



    @staticmethod
    def get_rating(soup_content):
        """ Получение рейтинга организации"""
        rating = ""
        try:
            elem = soup_content.find("div", {"class": "business-card-title-view__header-rating"})
            for data in elem.find_all("span", {"class": "business-rating-badge-view__rating-text"}):
                rating += data.getText()
            return rating
        except Exception as e:
            print('get_rating error '+getattr(e, 'message', repr(e)))
            return ""

    @staticmethod
    def get_reviews(soup_content, driver):
        """ Получение отзывов о организации"""
        print("Get reviews")

        driver.execute_script("document.getElementsByClassName('_name_reviews')[0].click();")
        sleep(1)

        reviews = []

        # Узнаём количество отзывов
        try:
            reviews_count = int(soup_content.find_all("div", {"class": "tabs-select-view__counter"})[-1].text)
            print("reviews count" + str(reviews_count))
        except ValueError:
            reviews_count = 0

        except AttributeError:
            reviews_count = 0

        except Exception:
            return ""

        if reviews_count > 150:
            find_range = range(100)
        else:
            find_range = range(30)

        for i in find_range:
            try:
                driver.execute_script("document.getElementsByClassName('scroll__container')[1].scrollTop="+str(500*i)+";")

            except MoveTargetOutOfBoundsException:
                break

        try:
            soup_content = BeautifulSoup(driver.page_source, "lxml")
            for data in soup_content.find_all("span", {"class": "business-review-view__body-text"}):
                reviews.append(data.getText())

            return reviews
        except Exception as e:
            print('get_reviews error '+getattr(e, 'message', repr(e)))
            return ""
