# -!- coding: utf-8 -!-

from tryy.base_class import Base

def cts_crawler(size=30):

    media = "華視"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}

    article_list = []

    temp_base = Base(title=None, content=None, category=None, modified_date=None, media=None)
    soup = temp_base.get_page('https://news.cts.com.tw/real/index.html', headers)
    sel = soup.select('div.newslist-container')
    sel = sel[0].find_all('a', href=True)

    urls = []
    for s in sel:
        urls.append(s['href'])
    # print(urls)

    news_count = 0
    for url in urls:
        instance = Base("Title", "Content", "Category", "Modified_Date", "華視", url=url, headers=headers)
        try:
            # print(url)
            soup = instance.url
            # print("success__getting__page")

            title_selector = 'h1.artical-title'
            title = instance.get_title(instance.url, title_selector)
            # print("success__getting__title: ", title)

            modified_date = soup.select("time.artical-time")
            modified_date = modified_date[0].text
            modified_date = instance.get_modified_date(modified_date)
            # print("success__getting__modified_date: ", modified_date)

            category_selector = 'div.item.menu-active'
            category = instance.get_category(soup, category_selector)[-1].text
            # print("success__getting__category: ", category)

            tags = []
            tags_span = soup.select("div.news-tag")[0].find_all('a')
            for tag in tags_span:
                tags.append(tag.text)
            # print("success__getting__tags: ", tags)

            content_selector = 'div.artical-content'
            content = instance.get_content(soup, content_selector, title)
            # print("success__getting__content: ", content)

            # print("success__getting__url_hash: ", instance.url_hash)
            # print("success__getting__cont_hash: ", instance.content_hash, "\n\n")

            news_dict = {}
            news_dict['title'] = title
            news_dict['content'] = content
            news_dict['category'] = category
            news_dict['modified_date'] = modified_date
            news_dict['media'] = media
            news_dict['tags'] = tags
            news_dict['url'] = url
            news_dict['url_hash'] = instance.url_hash
            news_dict['content_hash'] = instance.content_hash

            # print(news_dict)
            article_list.append(news_dict)

            news_count += 1
            if news_count >= size:
                break

        except Exception as e:
            print("華視 cts")
            print(url)
            print(e)
            continue

    return article_list

# result = cts_crawler(size=1)