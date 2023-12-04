# -!- coding: utf-8 -!-

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup

from test.base_class import Base


def ettoday_crawler(size=30):
    media = 'ettoday'
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}
    link = "https://www.ettoday.net/news/news-list.htm"

    article_list = []

    # initiate chrome webdriver
    options = Options()
    options.add_argument("--disable-notifications")
    options.headless = True

    driver = webdriver.Chrome('chromedriver', options=options)
    driver.get(link)
    
    for _ in range(1, 3):
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(3)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    sel = soup.find('div', 'part_list_2').find_all('h3')

    # exit selenium
    driver.quit()

    urls = []
    for s in sel:
        u = s.find('span')['href']
        urls.append("https://www.ettoday.net" + u)

    article_count = 0
    for url in urls:
        instance = Base("Title", "Content", "Category", "Modified_Date", "ettoday", url=url, headers=headers)
        try:
            soup = instance.get_page(instance.url, headers)

            # title = soup.find('h1', 'title').text
            title_selector = 'h1.title'
            title = instance.get_title(soup, title_selector)

            # modified_date = s.find('span').text
            modified_date = s.find('span').text
            modified_date = instance.get_modified_date(modified_date)

            # category = s.find('em').text
            category_selector = 'em'
            category = instance.get_category(soup, category_selector)

            tags = []
            tags = soup.find("meta", attrs={"name": "news_keywords"}).attrs['content'].split(',')

            article_content = []
            content_str = ""
            content_str += title
            for p in soup.find('div', 'story').find_all('p'):
                pText = p.text

                if '►' in pText or '▲' in pText or '·' in pText or pText == '' or '▼' in pText:
                    continue
                if '更多鏡週刊報導' in pText or '你可能也想看' in pText or '其他新聞' in pText or '其他人也看了' in pText or '更多新聞' in pText:
                    break

                article_content.append(p.text)
                content_str += p.text

            url_hash = instance.generate_hash(instance.url)
            content_hash = instance.generate_hash(article_content)

            news_dict = {
                'title': title,
                'content': article_content,
                'category': category,
                'modified_date': modified_date,
                'media': media,
                'tags': tags,
                'url': url,
                'url_hash': url_hash,
                'content_hash': content_hash
            }

            # print(news_dict)
            article_list.append(news_dict)

            article_count += 1
            if article_count >= size:
                break

        except Exception as e:
            print("ettoday")
            print(url)
            print(e)
            continue

    return article_list
