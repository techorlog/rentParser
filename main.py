import json
import os
import random

from undetected_chromedriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

import time
import keyboard
from urllib.parse import urlparse, urlunparse
import os
import requests

class Browser:
    site_dict = {"www.nhatot.com": None, "batdongsan.com.vn": None}

    def __init__(self):
        options = ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = Chrome(options=options)

        #a = self.webdriver.get(url)

    @classmethod
    def get_browser_instance(cls, url):
        site = urlparse(url).netloc
        if site in cls.site_dict:
            try:
                if isinstance(cls.site_dict[site], Browser):
                    return cls.site_dict[site]
                else:
                    cls.site_dict[site] = Browser() # насколько безопасно разрешать пользователю давать имя элементу словаря?
                    return cls.site_dict[site]
            except Exception as e:
                #if type(e) == UnboundLocalError:
                print(e)
                print(f"instance {site} is exists")

    def get_data(self, url):
        item_list = []
        index = url.rfind("=")
        left_url = url[:index + 1]
        #page = self.driver
        page = Browser.get_browser_instance(url)
        #current_html = WebDriverWait(page.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR,                                                                                         'main > div:first-child > div:last-child div >button[type="button"] > i'))))
        i = 0
        while True:
            i += 1
            url = left_url + str(i)
            page.driver.get(url)

            self.__scroll_down_page(page)
            page.driver.execute_script("""
                            var elem = document.elementFromPoint({x}, {y});
                            elem.click();
                            """.format(x=100, y=100))
            items = page.driver.find_elements(By.CSS_SELECTOR, 'main div.list-view div[role="button"] li > a')
            for element in items:
                item = self.__get_item(page, element)
                if item:
                    item_list.append(item)

            right_arrow_element = WebDriverWait(page.driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'main > div:first-child > div:last-child div > button[type="button"]')))  # current_html.find_element(By.CSS_SELECTOR, 'main > div:first-child > div:last-child div >button[type="button"] > i')
            child_element = right_arrow_element.find_element(By.CSS_SELECTOR, 'i')
            #child_element = page.driver.find_element(By.CSS_SELECTOR, 'i')
            is_next_page_exist = True if child_element.value_of_css_property("cursor") == "pointer" else False
            page.driver.execute_script("arguments[0].scrollIntoView(true);", right_arrow_element)
            page.driver.execute_script("window.scrollBy(0, -200);")
            time.sleep(0.5 + random.random()/2)
            if is_next_page_exist:
                # page.driver.execute_script("""
                # var elem = document.elementFromPoint({x}, {y});
                # elem.click();
                # """.format(x=100, y=100))
                right_arrow_element.click()
                print("clicked")
            else:
                break
        return item_list

    def __scroll_down_page(self, page):
        while True:
            try:
                page.driver.find_element(By.CSS_SELECTOR,
                                         'main > div:first-child > div:last-child div > button[type="button"] > i')
                break
            except NoSuchElementException as error:
                page.driver.execute_script(f"window.scrollBy(0, {300 + random.randint(100, 200)});")
                #print(error)
            except Exception as e:
                print(e)
                assert not e

    def __get_item(self, page, element):
        actions = ActionChains(page.driver)
        page.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        page.driver.execute_script("window.scrollBy(0, -300);")
        actions.key_down(Keys.CONTROL).click(element).key_up(Keys.CONTROL).perform()
        page.driver.switch_to.window(page.driver.window_handles[-1])
        time.sleep(5)
        try:
            item = Item(page.driver)
            # print(item.url)
            # print(item.item_id)
            # print(item.name)
            # print(item.phone_number)
            # print(item.price)
            # print(item.description)
            # print(item.address)
            #print(item.images_url_list)
            new_dict = item.__dict__.copy()
            del new_dict["driver"]
            json_data = json.dumps(new_dict, ensure_ascii=False)
            #json_data = json.dumps(new_dict, ensure_ascii=False).encode("utf-8")
            print(json_data)
            print(new_dict)
            if is_json_valid(json_data):
                #headers = {'Content-Type': 'application/json; charset=utf-8'}
                response = requests.post("http://localhost:8000/add_item", json=new_dict)
                print(response.status_code)
        except Exception as e:
            print(e)
        while len(page.driver.window_handles) > 1:
            page.driver.switch_to.window(page.driver.window_handles[-1])
            page.driver.close()
        page.driver.switch_to.window(page.driver.window_handles[0])
        #print(len(page.driver.find_elements(By.CSS_SELECTOR, 'main div.list-view div[role="button"] li > a')))
        return item

class Item:
    def __init__(self, driver): ### стоит ли делать return из функций и присваивать параметры в init
        self.driver = driver    #... так мы будем знать какие вообще есть свойства у класса, в разы удобнее читать.
        self.get_url()
        self.get_item_id()
        self.get_name()
        self.get_phone_number()
        self.get_address()
        self.get_price()
        self.get_description()
        #self.get_images()

    def get_url(self):
        parsed_url = urlparse(self.driver.current_url)
        self.url = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path

    def get_item_id(self):
        self.item_id = int(os.path.splitext(os.path.basename(urlparse(self.driver.current_url).path))[0])

    def get_name(self):
        css_selector = 'div[class="container"] div:first-child > div:first-child > div > div:first-child > div:nth-child(2) > div:first-child > h1'
        self.name = self.driver.find_element(By.CSS_SELECTOR, css_selector).text

    def get_phone_number(self):
        css_selector = "div.container > div:first-child > div:first-child > div:last-child > div > div:nth-child(2) > div:nth-child(2) > div:first-child > div:nth-child(2) > div:first-child"
        number_element = self.driver.find_element(By.CSS_SELECTOR, css_selector)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", number_element)
        number_element.click()
        css_selector = "div.container > div:first-child > div:first-child > div:last-child > div > div:nth-child(2) > div:nth-child(2) > div:first-child > div:nth-child(2) > div:first-child span"
        time.sleep(0.5)
        self.phone_number = self.driver.find_element(By.CSS_SELECTOR, css_selector).text

    def get_address(self):
        css_selector = 'div[class="container"] div:first-child > div:first-child > div:nth-child(4) > div:first-child > div:nth-child(2) > div:first-child > div:nth-child(2) > div:nth-child(2) > span > div > div:nth-child(2) div > span'
        address_element = self.driver.find_element(By.CSS_SELECTOR, css_selector)
        unwanted_element = address_element.find_element(By.CSS_SELECTOR, "span")
        self.driver.execute_script("arguments[0].remove();", unwanted_element)
        self.address = address_element.text

    def get_price(self):
        css_selector = 'div[class="container"] div:first-child > div:first-child > div > div:first-child > div:nth-child(2) > div:first-child span > div:first-child > span > span > span:first-child'
        price_element = self.driver.find_element(By.CSS_SELECTOR, css_selector)
        self.price = price_element.text

    def get_description(self):
        css_selector = 'body div.container > div:first-child > div:first-child > div:nth-child(4) > div:first-child > div:nth-child(4)  p'
        description_element = self.driver.find_element(By.CSS_SELECTOR, css_selector)
        self.description = description_element.text

    def get_images(self):
        css_selector = "div.slick-list > div.slick-track > div[data-index] span > img"
        pic_list = self.driver.find_elements(By.CSS_SELECTOR, css_selector)
        self.image_list = [_.get_attribute("src") for _ in pic_list]

def main():
    #url = "https://www.nhatot.com/thue-can-ho-chung-cu?f=p&page=1"
    url = "https://www.nhatot.com/thue-can-ho-chung-cu-thanh-pho-nha-trang-khanh-hoa?f=p&page=1"
    browser = Browser.get_browser_instance(url)
    item_list = browser.get_data(url)
    print(item_list)

    #element =
    keyboard.wait("|")


def is_json_valid(json_item):
    try:
        json.loads(json_item)
    except ValueError as e:
        print(e)
        return False
    return True


if __name__ == '__main__':
    main()
