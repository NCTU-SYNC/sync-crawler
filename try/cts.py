# -!- coding: utf-8 -!-

from base_class import Base

def cts_crawler(size=30):

    media = "華視"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}

    article_list = []

    urls = []
    try:
        soup = Base.get_page('https://news.cts.com.tw/real/index.html')
        newslist_str = "div.newslist-container"
        list_container = soup.select(newslist_str)
        a_list = list_container[0].find_all('a', href=True)
        for a_tag in a_list:
            urls.append(a_tag['href'])

    except Exception as e:
        print("cts")
        print("url list fetch error")
        print(e)

    news_count = 0
    for url in urls:
        instance = Base("Title", "Content", "Category", "Modified_Date", "華視", url=url, headers=headers)
        try:
            # soup = get_page(url)
            soup = instance.get_page(instance.url, headers)

            # title = soup.select("h1.artical-title")[0].text
            title_selector = 'h1.artical-title'
            title = instance.get_title(instance.url, title_selector)

            # date_text = soup.select("time.artical-time")[0].text
            # modified_date = datetime.datetime.strptime(date_text, "%Y/%m/%d %H:%M")
            # modified_date = utilities.convert_to_utc(modified_date)
            modified_date = soup.select("time.artical-time")[0].text
            modified_date = instance.get_modified_date(modified_date)

            # category = soup.select('div.item.menu-active')[-1].text
            category_selector = 'div.item.menu-active'
            category = instance.get_category(soup, category_selector)[-1].text

            # tags = []            
            # for a in soup.select("div.news-tag")[0].find_all('a'):
            #     tags.append(a.text)
            tags = []
            tags_span = soup.select("div.news-tag")[0].find_all('a')
            for tag in tags_span:
                tags.append(tag.text)

            content_selector = 'div.artical-content'
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

            news_count += 1
            if news_count >= size:
                break

        except Exception as e:
            print("cts")
            print(url)
            print(e)
            continue

    return article_list
