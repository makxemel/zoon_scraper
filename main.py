import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
from urllib.parse import unquote
import random
import json


headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
}


def get_source_html(url):

    service = Service('/home/makx/work/parsing/scrap_tutorial/zoon_scrap/chromedriver/chromedriver')
    driver = webdriver.Chrome(service=service)

    driver.maximize_window()

    try:
        driver.get(url=url)
        time.sleep(3)

        SCROLL_PAUSE_TIME = 0.5

        # Get scroll height
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                with open("source-page.html", "w") as file:
                    file.write(driver.page_source)
                break
            last_height = new_height
    except Exception as _ex:
        print(_ex)


def get_items_urls(file_path):
    with open(file_path) as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")
    items_divs = soup.find_all("div", class_="minicard-item__container")

    urls = []
    for item in items_divs:
        item_url = item.find("h2").find("a").get("href")
        urls.append(item_url)

    with open("items_urls.txt", "w") as file:
        for url in urls:
            file.write(f"{url}\n")

    return "[INFO] URL'S COLLECTED SUCCESSFULLY!"


def get_data(file_path):
    with open(file_path) as file:

     urls_list = [url.strip() for url in file.readlines()]

    result_list = []
    urls_count = len(urls_list)
    count = 1
    for url in urls_list:
        response = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")

        try:
            item_name = soup.find("span", {"itemprop": "name"}).text.strip()
        except Exception as ex:
            item_name = None

        item_phones_list = []
        try:
            item_phones = soup.find("div", class_="service-phones-list").find_all("a", class_="js-phone-number")

            for phone in item_phones:
                item_phone = phone.get("href").split(":")[-1].strip()
                item_phones_list.append(item_phone)
        except Exception as ex:
            item_phone = None

        try:
            item_address = soup.find("address", class_="iblock").text.strip()
        except Exception as ex:
            item_address = None

        try:
            item_site = soup.find("div", class_="service-website-value").text.strip()
        except Exception as ex:
            item_site = None

        social_newtworks_list = []
        try:
            item_socialnetwork = soup.find("div", class_="service-description-social-list").find_all("a")

            for sn in item_socialnetwork:
                url_sn = sn.get("href")
                url_sn_clear = unquote(url_sn.split("?to=")[1].split("&")[0])
                social_newtworks_list.append(url_sn_clear)
        except Exception as ex:
            item_socialnetwork = None

        result_list.append({
            "item_name": item_name,
            "item_url": url,
            "item_phones_list": item_phones_list,
            "item_address": item_address,
            "item_site": item_site,
            "social_newtworks_list": social_newtworks_list,

        })

        time.sleep(random.randrange(2, 5))
        count += 1
        if count%10 == 0:
            time.sleep(random.randrange(2, 9))

        print(f"[+] Processed {count}/{urls_count}")

    with open("result.json", "w") as file:
        json.dump(result_list, file, indent=4, ensure_ascii=False)

    return "[INFO] Data collected successfully!"



def main():
    # get_source_html(url="https://spb.zoon.ru/medical/type/detskaya_poliklinika/")
    # print(get_items_urls('source-page.html'))
    # get_data('items_urls.txt')


if __name__ == "__main__":
    main()
