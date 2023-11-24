# -!- coding: utf-8 -!-

from base_class import Base


def chinatimes_crawler(size=30):

    media = '中時'
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}

    article_list = []

    #retrieve news list for first five pages
    links = ['https://www.chinatimes.com/realtimenews/','https://www.chinatimes.com/realtimenews/?page=2',
            'https://www.chinatimes.com/realtimenews/?page=3','https://www.chinatimes.com/realtimenews/?page=4',
            'https://www.chinatimes.com/realtimenews/?page=5']
    urls = []
    for link in links:
        soup = Base.get_page(link)
        # soup = get_page(link)
        sel = soup.find_all('div', class_='articlebox-compact')

        for s in sel:
            u = s.find(class_='title').find('a')['href']
            urls.append('https://www.chinatimes.com'+u)

    news_count = 0
    for url in urls:
        instance = Base("Title", "Content", "Category", "Modified_Date", "中時", url=url, headers=headers)
        try:
            # soup = get_page(url)
            soup = instance.get_page(instance.url, headers)

            # title = soup.find(class_='article-title').text
            title_selector = '.article-title'
            title = instance.get_title(instance.url, title_selector)

            date_tag = soup.find('time') #time
            modified_date = date_tag.find(class_='hour').text + ' ' + date_tag.find(class_='date').text #full date
            # modified_date = datetime.datetime.strptime(modified_date, "%H:%M %Y/%m/%d")
            # modified_date = utilities.convert_to_utc(modified_date)
            modified_date = instance.get_modified_date(modified_date)

            # category = soup.find_all(class_='breadcrumb-item')[1].text.strip()
            category_selector = '.breadcrumb-item'
            category = instance.get_category(soup, category_selector)[1].text.strip()
            
            tags_span = soup.find_all(class_='hash-tag')
            tags = []
            for tag in tags_span:
                cur_tag = tag.text.strip()
                cur_tag = cur_tag[1:]
                tags.append(cur_tag)

            # content = []
            # content_str = ""
            # content_str += title
            # article_body = soup.find(class_='article-body').find_all('p')
            # for p in article_body:
            #     part = p.text
            #     #skip if empty
            #     if not part:
            #         continue
            #     content.append(part)
            #     content_str += part
            content_selector = '.article-body'
            # content = instance.get_content(soup, class_='article-body',title)
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
            # print('\n)
            article_list.append(news_dict)

            news_count+=1

            if news_count >= size:
                break
            
        except Exception as e:
            print('chinatimes')
            print(url)
            print(e)
            continue
    
    return article_list