# -!- coding: utf-8 -!-

import requests
from test.base_class import Base

link = 'https://news.ltn.com.tw/ajax/breakingnews/all/1'
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}

def get_one_page(url):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print("Page fetch failed:", e)

def parse_data(urls):
    first = True
    count = 20
    for url in link:
        # obtain json from ltnnews ajax
        data = get_one_page(url)
        # page1 and remaining pages are in different format, therefore different strategies applied
        if first:
            # 'data' is in the form of a list of articles, for each article, obtain url
            for article in data['data']:
                urls.append(article['url'])
        else:
            try:
                for _ in range(20):
                    number = str(count)
                    urls.append(data['data'][number]['url'])
                    count += 1
            except TypeError as e:
                print('Parse data error!')
                print(e)
    first = False

def ltn_crawler(size=10):
    media = '自由時報'
    article_list = []

    categories = {'health': '健康', 'video': '影音', 'ec': '財經', 'ent': '娛樂', 'auto': '汽車', 'istyle': '時尚', 'sports': '體育',
                  '3c': '3C科技', 'talk': '評論', 'playing': '玩咖', 'food': '食譜', 'estate': '地產'}
    
    urls = []
    parse_data(urls)

    article_count = 0
    for url in urls:
        instance = Base("Title", "Content", "Category", "Modified_Date", "自由時報", url=url, headers=headers)
        try:
            soup = instance.get_page(instance.url, headers)
            title_selector = 'h1'
            title = instance.get_title(soup, title_selector)
            modified_date = soup.find('span', 'time').text.strip()[:16]
            modified_date = instance.get_modified_date(modified_date)

            start = url.find('//') + 2
            link_cat = url[start:url.find('.')]
            if categories.get(link_cat):
                category = categories[link_cat]
            else:
                try:
                    category_selector = 'div.breadcrumbs.boxTitle.boxText'
                    category = instance.get_category(soup, category_selector)[0].text
                    category = category[6:].strip()
                except AttributeError:
                    print('Error when finding category.')
                    raise AttributeError

            tags = []
            content = []
            content_str = ""
            content_str += title
            try:
                allpara = soup.find('div', attrs={'data-desc': '內容頁'}).find_all('p')
                pcount = len(allpara)
            except AttributeError:
                allpara = soup.find('div', attrs={'data-desc': '內文'}).find_all('p')
                pcount = len(allpara)

            for p in allpara:
                if pcount == 1:
                    break
                para = p.text
                if '請繼續往下閱讀' in para:
                    continue
                content.append(p.text)
                content_str += p.text
                pcount -= 1

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
            print("自由時報 ltn")
            print(url)
            print(e)
            continue

    return article_list
