# -!- coding: utf-8 -!-

from test.base_class import Base

def storm_crawler(size=10):

    media = '風傳媒'
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}

    article_list = []

    links = ["https://www.storm.mg/articles", "https://www.storm.mg/articles/2",
             "https://www.storm.mg/articles/3", "https://www.storm.mg/articles/4",
             "https://www.storm.mg/articles/5", "https://www.storm.mg/articles/6"]

    for link in links:
        soup = Base.get_page(link)
        sel = soup.find_all('div', 'category_card card_thumbs_left')

        urls = []
        for s in sel:
            u = s.find('a')['href']
            urls.append(u)

        article_count = 0
        for url in urls:
            instance = Base("Title", "Content", "Category", "Modified_Date", "風傳媒", url=url, headers=headers)
            try:
                soup = instance.get_page(instance.url, headers)

                # title = soup.find('h1', id='article_title').text
                title_selector = 'h1#article_title'
                title = instance.get_title(soup, title_selector)

                modified_date = soup.find('span', id='info_time').text
                modified_date = instance.get_modified_date(modified_date)

                # sel = soup.find('div', id='title_tags_wrapper')
                # for s in sel.find_all('a'):
                category_selector = 'div#title_tags_wrapper a'
                category = instance.get_category(soup, category_selector)

                tags = []

                # para = soup.find('div', id='CMS_wrapper').find_all('p')
                content_selector = 'div#CMS_wrapper p'
                content = instance.get_content(soup, content_selector, title)

                url_hash = instance.generate_hash(instance.url)
                content_hash = instance.generate_hash(content)

                news_dict = {
                    'title': title,
                    'content': content,
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
                print("風傳媒 storm")
                print(url)
                print(e)
                continue

    return article_list
