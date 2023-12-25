# -!- coding: utf-8 -!-

from tryy.base_class import Base

def storm_crawler(size=10):

    media = '風傳媒'
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}

    article_list = []

    links = ["https://www.storm.mg/articles", "https://www.storm.mg/articles/2",
             "https://www.storm.mg/articles/3", "https://www.storm.mg/articles/4",
             "https://www.storm.mg/articles/5", "https://www.storm.mg/articles/6"]

    temp_base = Base(title=None, content=None, category=None, modified_date=None, media=None)

    for link in links:
        soup = temp_base.get_page(link, headers)
        sel = soup.find_all('div', 'category_card card_thumbs_left')

    urls = []
    for s in sel:
        u = s.find('a')['href']
        urls.append(u)
    # print(urls)

    article_count = 0
    for url in urls:
        instance = Base("Title", "Content", "Category", "Modified_Date", "風傳媒", url=url, headers=headers)
        try:
            # print(url)
            soup = instance.url
            # print("success__getting__page")
            # print(soup)

            title_selector = '#article_title'
            title = instance.get_title(soup, title_selector)
            # print("success__getting__title: ", title)

            modified_date = soup.find('span', id='info_time').text
            modified_date = instance.get_modified_date(modified_date)
            # print("success__getting__modified_date: ", modified_date)
            
            category = []
            category_selector = 'a.tags_link'
            category_set = instance.get_category(soup, category_selector)
            for a in category_set:
                a = a.get_text()
                if a not in ['評論', '投書', '專欄']:
                    category.append(a)
            # print("success__getting__category: ", category)

            tags = []
            tag_links = soup.select('div#tags_list_wrapepr a')
            for tag in tag_links:
                tags.append(tag.get_text())
            # print("success__getting__tags: ", tags)

            content_selector = '#CMS_wrapper p'
            content = instance.get_content(soup, content_selector, title)
            # print("success__getting__content: ", content)

            # print("success__getting__url_hash: ", instance.url_hash)
            # print("success__getting__cont_hash: ", instance.content_hash, "\n\n")

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

            print(news_dict)
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

# result = storm_crawler(size=1)
