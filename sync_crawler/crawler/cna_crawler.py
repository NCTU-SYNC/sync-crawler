from proto.news_pb2 import News
from sync_crawler.crawler.base_crawler import BaseCrawler


class CnaCrawler(BaseCrawler):

    def __init__(self, custom_property, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def cna_urls(self, headers):
        url = 'https://www.cna.com.tw/list/aall.aspx'
        soup = self.get_page(url, headers)
        sel = soup.find('ul', 'mainList imgModule',
                        id='jsMainList').find_all('li')
        urls = [s.find('a')['href'] for s in sel if s.find('a')]
        return urls

    def cna_modified_date(self, soup):
        modified_date = soup.find('div', class_='updatetime').text
        modified_date = self.get_modified_date(modified_date)
        return modified_date

    def cna_category(self, soup):
        category_selector = 'div.breadcrumb a'
        category = self.get_category(soup, category_selector)
        category = category[1].text
        return category

    def cna_tag(self, soup):
        tag_links = soup.select('div.keywordTag a')
        tags = [tag.get_text().replace('#', '') for tag in tag_links]
        return tags

    def cna_content(self, soup, title):
        content = soup.find("div", class_="paragraph")
        content_selector = 'p:lang(zh)'
        content = self.get_content(content, content_selector, title)
        return content