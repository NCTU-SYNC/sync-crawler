# -!- coding: utf-8 -!-

from test.base_class import Base

def ebc_crawler(size=30):

    media = '東森'
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}

    article_list = []

    links = ['https://news.ebc.net.tw/realtime', 'https://news.ebc.net.tw/realtime?page=2',
             'https://news.ebc.net.tw/realtime?page=3', 'https://news.ebc.net.tw/realtime?page=4']
    urls = []
    for link in links:
        soup = Base.get_page(link)
        sel = soup.find('div', 'news-list-box').find_all('div', 'style1 white-box')  # get news list

        for s in sel:
            u = s.find('a')['href']
            urls.append('https://news.ebc.net.tw' + u)

    news_count = 0
    for url in urls:
        instance = Base("Title", "Content", "Category", "Modified_Date", "東森", url=url, headers=headers)
        try:
            soup = instance.get_page(instance.url, headers)

            # title = soup.find('div', 'fncnews-content').find('h1').text
            title_selector = 'div.fncnews-content h1'
            title = instance.get_title(instance.url, title_selector)

            date_tag = soup.find('span', 'small-gray-text').text
            date_tag = date_tag.split()
            modified_date = date_tag[0] + ' ' + date_tag[1]
            modified_date = instance.get_modified_date(modified_date)

            # category = soup.find('div', id = 'web-map').find_all('a')[1].text
            category_selector = 'div#web-map a'
            category = instance.get_category(soup, category_selector)[1].text

            # try:
            #     sel = soup.find('div', 'keyword').find_all('a')
            #     for s in sel:
            #         tags.append(s.text)
            # except:
            #     tags = []
            tags = []
            tags_span = soup.find('div', 'keyword').find_all('a')
            for tag in tags_span:
                tags.append(tag.text)

            # content_sel = soup.find('div', 'raw-style').find_all('p')
            # content_selector = 'div.raw-style p'
            # content = instance.get_content(soup, content_selector)

            content_sel = soup.find('div', 'raw-style').find_all('p')
            content = []
            content_str = ""
            content_str += title
            for p in content_sel:
                content_part = p.text
                # clear unwanted content
                if content_part.startswith('★') or not content_part or '延伸閱讀' in content_part:
                    continue
                if '\u3000' in content_part:
                    content_part.replace('\u3000', ' ')
                if '\xa0' == content_part:
                    continue
                content.append(content_part.strip())
                content_str += content_part.strip()

            url_hash = instance.generate_hash(instance.url)
            content_hash = instance.generate_hash(content_str)

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
            print("東森ebc")
            print(url)
            print(e)
            continue

    return article_list
