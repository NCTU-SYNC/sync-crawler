# -!- coding: utf-8 -!-
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
import hashlib

# class get_mutiple_link:

#     def ___init__(self, link)
#         self.link = link

#     def get_page

class Base:

    def __init__(self, title, content, category, modified_date, media, url=None, url_hash=None, content_hash=None, headers=None):
        self.title = title
        self.content = content
        self.category = category
        self.modified_date = self.get_modified_date(modified_date)
        self.media = media
        # self.tags = tags
        self.url = self.get_page(url, headers)
        self.url_hash = url_hash if url_hash else self.generate_hash(url)
        self.content_hash = content_hash if content_hash else self.generate_hash(content)

    def get_page(self, url, headers):
        try:
            r = requests.get(url, headers)
            r.encoding = 'UTF-8'
            soup = BeautifulSoup(r.text, "html.parser")
            return soup
        except requests.RequestException as e:
            print(f"Error fetching page: {e}")
            return None

    def get_title(self, soup, title_sel):
        # title = soup.select(title_sel)
        title = soup.find(title_sel).text
        return title

    def get_content(self, soup, content_sel, title):
        content_sel = soup.select(content_sel)
        article_content = []
        content_str = ""
        content_str += title
        for s in content_sel:
            article_content.append(s.text)
            content_str += s.text
        return article_content

    def get_category(self, soup, category_sel):
        category = soup.select(category_sel)
        return category

    def get_modified_date(self, date_text):
        modified_date = datetime.strptime(date_text, "%Y/%m/%d %H:%M")
        tz = timezone(timedelta(hours=+8))
        modified_date = modified_date.replace(tzinfo=tz)
        modified_date = modified_date.astimezone(tz)
        modified_date = modified_date.astimezone(timezone.utc)
        return modified_date

    # def get_tags(self, soup, tag_key, tag_sel):
    #     tags = []
    #     if tag_key:
    #         tag_sel = soup.select(tag_sel)
    #         for t in tag_sel:
    #             tags.append(t.text)
    #     return tags

    def generate_hash(self, data):
        result = hashlib.sha1(data.encode('utf-8'))
        return result.hexdigest()

