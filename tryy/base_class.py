import requests
from bs4 import BeautifulSoup
import hashlib
from abc import ABC, abstractmethod

class BaseCrawler(ABC):

    def __init__(self, title, content, category, modified_date, media, url=None, url_hash=None, content_hash=None, headers=None):
        self.title = title
        self.content = content
        self.category = category
        self.modified_date = self.get_modified_date(modified_date)
        self.media = media
        self.url = self.get_page(url, headers)
        self.url_hash = url_hash if url_hash else self.generate_hash(url) if url else None
        self.content_hash = content_hash if content_hash else self.generate_hash(content) if content else None

    @abstractmethod
    def get_page(self, url, headers):
        try:
            r = requests.get(url, headers)
            r.encoding = 'UTF-8'
            soup = BeautifulSoup(r.text, "html.parser")
            if soup is None:
                print("Soup object is None. Parsing failed.")
            return soup
        except requests.RequestException as e:
            print(f"Error fetching page")
            return None

    def get_title(self, soup, title_sel):
        title = soup.select_one(title_sel)
        title = title.text
        return title

    def get_content(self, soup, content_sel, title):
        content_sel = soup.select(content_sel)
        article_content = []
        content_str = ""
        content_str += title
        for s in content_sel:
            s = s.text.replace('\n', '')
            article_content.append(s)
            content_str += s
        return article_content

    def get_category(self, soup, category_sel):
        category = soup.select(category_sel)
        return category
    
    def find_category(self, soup, type, class_):
        category = soup.find_all(type, class_=class_)
        for c in category:
            print(c.text(), " ")
        return category

    def get_modified_date(self, date_text):
        try:
            date_text = date_text.strip()
            if ":" in date_text and len(date_text.split(":")) == 3:
                date_text = ':'.join(date_text.split(':')[:-1])
            if '-' in date_text:
                date_text = date_text.replace('-', '/')
            if ' ' not in date_text:
                date_text += " 00:00"
            return date_text[:16]
        except Exception as e:
            print(f"Error getting modified date {e}")
            return None

    def generate_hash(self, data):
        result = hashlib.sha1(data.encode('utf-8'))
        return result.hexdigest()

