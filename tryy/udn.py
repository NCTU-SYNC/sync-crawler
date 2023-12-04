# -!- coding: utf-8 -!-

from test.base_class import Base

def udn_crawler(size=10):

    media = '聯合'
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}

    article_list = []

    link = 'https://tfc-taiwan.org.tw/articles/report'
    urls = []
    soup = Base.get_page(link)
    sel = soup.find_all('div', class_='view-content')

    for s in sel:
        u = s.find('a')['href']
        urls.append('https://tfc-taiwan.org.tw' + u)

    article_count = 0
    for url in urls:
        instance = Base("Title", "Content", "Category", "Modified_Date", "聯合", url=url, headers=headers)
        try:
            soup = instance.get_page(instance.url, headers)

            title_selector = 'article-content__title'
            title = instance.get_title(soup, title_selector)

            modified_date = soup.find(class_='article-content__time').text
            modified_date = instance.get_modified_date(modified_date)

            # category = soup.find_all(class_='breadcrumb-items')[1].text
            category_selector = '.breadcrumb-items'
            category = instance.get_category(soup, category_selector)[1].text.strip()

            tags = []

            # article_body = soup.find(class_='article-content__editor').find_all('p')
            content_selector = '.article-content__editor p'
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
            print("聯合 udn")
            print(url)
            print(e)
            continue

    return article_list
