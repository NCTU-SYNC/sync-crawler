# -!- coding: utf-8 -!-

from test.base_class import Base

def setn_crawler(size=10):

    media = '三立'
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}

    article_list = []

    view_all_link = "https://www.setn.com/ViewAll.aspx"
    base = 'https://www.setn.com'

    soup = Base.get_page(view_all_link)
    sel = soup.find_all('h3', class_='view-li-title')

    urls = []
    for s in sel:
        u = s.a['href']
        if u[0] == '/':
            full_url = base + u
        else:
            full_url = u
        urls.append(full_url)

    article_count = 0
    for url in urls:
        instance = Base("Title", "Content", "Category", "Modified_Date", "三立", url=url, headers=headers)
        try:
            soup = instance.get_page(instance.url, headers)

            title_selector = 'h1'
            title = instance.get_title(soup, title_selector)

            try:
                modified_date = soup.find('time', class_='page-date').text
            except AttributeError:
                modified_date = soup.find(class_='newsTime').time.text
            modified_date = instance.get_modified_date(modified_date)

            category_selector = 'meta[property="article:section"]'
            category = instance.get_category(soup, category_selector)[0]['content']

            tags = []
            tags = soup.find('meta', attrs={'name': 'news_keywords'})['content'].split(',')

            content_selector = 'article p'
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
            print("三立 setn")
            print(url)
            print(e)
            continue

    return article_list
