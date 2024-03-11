from proto.news_pb2 import News
from sync_crawler.crawler.base_crawler import BaseCrawler

url = 'https://www.cna.com.tw/list/aall.aspx'


class CtsCrawler(BaseCrawler):

    def cts_urls(self, timeout: int):
        soup = self.get_page(url, timeout)
        sel = soup.select('div.newslist-container')
        sel = sel[0].find_all('a', href=True)
        urls = []
        for s in sel:
            urls.append(s['href'])
        return urls

    def cts_modified_date(self, soup):
        modified_date = soup.select("time.artical-time")
        modified_date = modified_date[0].text
        modified_date = self.get_modified_date(modified_date)
        return modified_date

    def cts_modified_date(self, soup):
        category_selector = 'div.item.menu-active'
        category = self.get_category(soup, category_selector)[-1].text
        return category

    def cts_tag(self, soup):
        tags = []
        tags_span = soup.select("div.news-tag")[0].find_all('a')
        for tag in tags_span:
            tags.append(tag.text)
        return tags

    def cts_content(self, soup, title: str):
        content_selector = 'div.artical-content'
        content = self.get_content(soup, content_selector, title)
        return content
