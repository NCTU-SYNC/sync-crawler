# -!- coding: utf-8 -!-

from tryy.base_class import Base

def cna_crawler(size=30):

    media = '中央社'
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}
    
    article_list = []

    temp_base = Base(title=None, content=None, category=None, modified_date=None, media=None)
    soup = temp_base.get_page('https://www.cna.com.tw/list/aall.aspx', headers)
    sel = soup.find('ul', 'mainList imgModule', id='jsMainList').find_all('li')

    urls = []
    for s in sel:
        urls.append(s.find('a')['href'])
    # print(urls)

    news_count = 0
    for url in urls:
        instance = Base("Title", "Content", "Category", "Modified_Date", "中央社", url=url, headers=headers)
        try:
            # print(url)
            soup = instance.url
            # print("success__getting__page")

            title_selector = 'div.centralContent h1'
            title = instance.get_title(soup, title_selector)
            # print("success__getting__title: ", title)

            modified_date = soup.find('div', class_='updatetime').text
            modified_date = instance.get_modified_date(modified_date)
            # print("success__getting__modified_date: ", modified_date)

            category_selector = 'div.breadcrumb a'
            category = instance.get_category(soup, category_selector)
            category = category[1].text
            # print("success__getting__category: ", category)

            tags = []
            tag_links = soup.select('div.keywordTag a')
            for tag in tag_links:
                tag = tag.get_text()
                tag = tag.replace('#', '')
                tags.append(tag)
            # print("success__getting__tags: ", tags)

            content = soup.find("div", class_="paragraph")
            content_selector = 'p:lang(zh)'
            content = instance.get_content(content, content_selector, title)
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
            print("中央社cna")
            print(url)
            print(e)
            continue

    return article_list

# result = cna_crawler(size=1)