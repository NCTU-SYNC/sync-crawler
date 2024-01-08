# -!- coding: utf-8 -!-

from proto.news_pb2 import News
from tryy.base_class import BaseCrawler


def cna_crawler(size=30):

    media = '中央社'
    headers = {
        "User-Agent":
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    article_list = []

    temp_base = BaseCrawler(title=None,
                            content=None,
                            category=None,
                            modified_date=None,
                            media=None)
    soup = temp_base.get_page('https://www.cna.com.tw/list/aall.aspx', headers)
    sel = soup.find('ul', 'mainList imgModule', id='jsMainList').find_all('li')

    urls = [s.find('a')['href'] for s in sel if s.find('a')]

    news_count = 0
    for url in urls:
        instance = BaseCrawler("Title",
                               "Content",
                               "Category",
                               "Modified_Date",
                               "中央社",
                               url=url,
                               headers=headers)
        try:
            soup = instance.url

            title_selector = 'div.centralContent h1'
            title = instance.get_title(soup, title_selector)

            modified_date = soup.find('div', class_='updatetime').text
            modified_date = instance.get_modified_date(modified_date)

            category_selector = 'div.breadcrumb a'
            category = instance.get_category(soup, category_selector)
            category = category[1].text

            tag_links = soup.select('div.keywordTag a')
            tags = [tag.get_text().replace('#', '') for tag in tag_links]

            content = soup.find("div", class_="paragraph")
            content_selector = 'p:lang(zh)'
            content = instance.get_content(content, content_selector, title)

            news_item = News()
            news_item.title = title
            news_item.content = content
            news_item.category = category
            news_item.modified_date = modified_date
            news_item.media = media
            news_item.tags.extend(tags)
            news_item.url = url
            news_item.url_hash = instance.url_hash
            news_item.content_hash = instance.content_hash

            yield news_item
            news_count += 1

            if news_count >= size:
                break

        except Exception as e:
            print("中央社cna")
            print(url)
            print(e)
