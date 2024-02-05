1  # -!- coding: utf-8 -!-

from tryy.base_class import BaseCrawler


def setn_crawler(size=10):

    print("in setn")

    media = '三立'
    headers = {
        "User-Agent":
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    article_list = []

    view_all_link = "https://www.setn.com/ViewAll.aspx"
    base = 'https://www.setn.com'

    temp_base = BaseCrawler(title=None,
                            content=None,
                            category=None,
                            modified_date=None,
                            media=None)

    soup = temp_base.get_page(view_all_link, headers)
    sel = soup.find_all('a', class_='gt')

    urls = []
    for s in sel:
        u = s.get('href')
        if u[0] == '/':
            full_url = base + u
        else:
            full_url = u
        urls.append(full_url)

    article_count = 0
    for url in urls:
        instance = BaseCrawler("Title",
                               "Content",
                               "Category",
                               "Modified_Date",
                               "三立",
                               url=url,
                               headers=headers)
        try:
            # print(url)
            soup = instance.url
            # print("success__getting__page")

            title_selector = 'h1.news-title-3'
            title = instance.get_title(soup, title_selector)
            # print("success__getting__title: ", title)

            try:
                modified_date = soup.select_one('div.page-title-text')
                modified_date = modified_date.text
            except AttributeError:
                modified_date = soup.find(class_='newsTime').time.text
            modified_date = instance.get_modified_date(modified_date)
            # print("success__getting__modified_date: ", modified_date)

            category_selector = 'meta[property="article:section"]'
            category = instance.get_category(soup,
                                             category_selector)[0]['content']
            # print("success__getting__category: ", category)

            tags = []
            tags = soup.find('meta', attrs={'name': 'news_keywords'
                                           })['content'].split(',')
            # print("success__getting__tags: ", tags)

            content_selector = 'article p'
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
            print("三立 setn")
            print(url)
            print(e)
            continue

    return article_list


# print("import success")
result = setn_crawler(size=1)
