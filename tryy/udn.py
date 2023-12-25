# -!- coding: utf-8 -!-

from tryy.base_class import Base
import re

def udn_crawler(size=10):

    print("in udn")

    media = '聯合'
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}

    article_list = []

    link = 'https://tfc-taiwan.org.tw/articles/report'
    urls = []

    temp_base = Base(title=None, content=None, category=None, modified_date=None, media=None)
    
    soup = temp_base.get_page(link, headers)
    sel = soup.find('div', class_='view-content')
    sel = soup.find_all('h3', class_='entity-list-title')
    
    for s in sel:
        temp = s.find('a')
        u = temp.get('href')
        urls.append('https://tfc-taiwan.org.tw' + u)
    # print(urls)

    article_count = 0
    for url in urls:
        instance = Base("Title", "Content", "Category", "Modified_Date", "聯合", url=url, headers=headers)
        try:
            # print(url)
            soup = instance.url
            # print("success__getting__page")

            title_selector = 'h2.node-title'
            title = instance.get_title(soup, title_selector)
            # print("success__getting__title: ", title)

            modified_date = soup.select_one('div.submitted')
            modified_date = modified_date.text
            modified_date = instance.get_modified_date(modified_date)
            # print("date: ", modified_date)

            category = []
            category_select = soup.find("div", class_="node-tags")
            a_elements = category_select.find_all("a")
            for a in a_elements:
                if (a.text != '事實查核報告'):
                    category.append(a.text)
            # print("success__getting__category: ", category)

            tags = []

            content = soup.find("div", class_="node-content")
            content_selector = 'p:lang(zh)'
            content = instance.get_content(content, content_selector, title)
            # print("success__getting__content: ", content)

            # print("success__getting__url_hash: ", instance.url_hash)
            # print("success__getting__cont_hash: ", instance.content_hash)

            news_dict = {
                'title': title,
                'content': content,
                'category': category,
                'modified_date': modified_date,
                'media': media,
                'tags': tags,
                'url': url,
                'url_hash': instance.url_hash,
                'content_hash': instance.content_hash
            }

            # print(news_dict)
            article_list.append(news_dict)

            article_count += 1

            if article_count >= size:
                break

        except Exception as e:
            print("聯合 udn")
            print(url)
            print(e)
            continue

    return article_list

# result = udn_crawler(size=1)
