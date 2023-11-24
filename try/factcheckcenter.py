# -!- coding: utf-8 -!-

from test.base_class import Base

def factcheckcenter_crawler(size=10):

    media = '台灣事實查核中心'
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
        instance = Base("Title", "Content", "Category", "Modified_Date", "台灣事實查核中心", url=url, headers=headers)
        try:
            soup = instance.get_page(instance.url, headers)

            title_selector = 'h2.node-title'
            title = instance.get_title(soup, title_selector)[0].text

            modified_date = soup.find('div', 'submitted').text
            modified_date = instance.get_modified_date(modified_date)

            # category = soup.find('div','field-name-field-taxo-report-attr').text.strip()
            category_selector = 'div.field-name-field-taxo-report-attr'
            category = instance.get_category(soup, category_selector)[0].text.strip()

            tags = []

            # para = soup.find('div', 'field field-name-body field-type-text-with-summary field-label-hidden').find_all(['p','h2']) #get headings and content
            content_selector = 'div.field.field-name-body.field-type-text-with-summary.field-label-hidden p, div.field.field-name-body.field-type-text-with-summary.field-label-hidden h2'
            content = instance.get_content(soup, content_selector, title)

            url_hash = instance.generate_hash(instance.url)
            content_hash = instance.generate_hash(content)

            news_dict = {}
            news_dict['title'] = title
            news_dict['content'] = content
            news_dict['category'] = category
            news_dict['modified_date'] = modified_date
            news_dict['media'] = media
            news_dict['tags'] = tags
            news_dict['url'] = url
            news_dict['url_hash'] = url_hash
            news_dict['content_hash'] = content_hash

            # print(news_dict)
            article_list.append(news_dict)

            article_count += 1

            if article_count >= size:
                break

        except Exception as e:
            print("台灣事實查核中心 factcheckcenter")
            print(url)
            print(e)
            continue

    return article_list
