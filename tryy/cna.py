# -!- coding: utf-8 -!-

from test.base_class import Base

def cna_crawler(size=30):

    media = '中央社'
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}
    
    article_list = []

    # soup = get_page('https://www.cna.com.tw/list/aall.aspx')
    soup = Base.get_page('https://www.cna.com.tw/list/aall.aspx')
    sel = soup.find('ul', 'mainList imgModule', id='jsMainList').find_all('li')

    # add each url to url list
    urls = []
    for s in sel:
        urls.append(s.find('a')['href'])

    news_count = 0
    for url in urls:
        instance = Base("Title", "Content", "Category", "Modified_Date", "中央社", url=url, headers=headers)
        try:
            # soup = get_page(url)
            soup = instance.get_page(instance.url, headers)

            # title = soup.find('div', 'centralContent').find('h1').text
            title_selector = 'div.centralContent h1'
            title = instance.get_title(instance.url, title_selector)

            modified_date = soup.find('meta', itemprop='dateModified')['content']
            # modified_date = datetime.datetime.strptime(modified_date, "%Y/%m/%d %H:%M")
            # modified_date = utilities.convert_to_utc(modified_date)
            modified_date = instance.get_modified_date(modified_date)

            # category = soup.find('div', 'breadcrumb').find_all('a')[1].text
            category_selector = 'div.breadcrumb a'
            category = instance.get_category(soup, category_selector)[1].text

            tags = []

            # article_content = []
            # content_str = ""
            # content_str += title
            # sel = soup.find('div', 'paragraph').find_all('p')
            # for s in sel:
            #     article_content.append(s.text)
            #     content_str += s.text
            content_selector = 'div.paragraph p'
            content = instance.get_content(soup, content_selector, title)

            # url_hash = generate_hash(url)
            url_hash = instance.generate_hash(instance.url)
            # content_hash = generate_hash(content_str)
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

            news_count += 1

            if news_count >= size:
                break

        except Exception as e:
            print("中央社cna")
            print(url)
            print(e)
            continue

    return article_list
