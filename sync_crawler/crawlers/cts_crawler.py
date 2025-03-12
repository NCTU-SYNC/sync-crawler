from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime

import bs4
import requests
from dateutil.parser import parse

from sync_crawler.crawlers.base_crawler import BaseCrawler
from sync_crawler.models.news import News


@dataclass
class CtsNewsMetadata:
    publish_time: datetime
    category: str | None
    url: str


class CtsCrawler(BaseCrawler):
    media_name = "cts"
    metadata_api = "https://news.cts.com.tw/real/index.html"
    category_mapping = {
        "https://static.cts.com.tw/news/images/icon-international.png": "國際",
        "https://static.cts.com.tw/news/images/icon-life.png": "生活",
        "https://static.cts.com.tw/news/images/icon-society.png": "社會",
        "https://static.cts.com.tw/news/images/icon-general.png": "綜合",
        "https://static.cts.com.tw/news/images/icon-politics.png": "政治",
        "https://static.cts.com.tw/news/images/icon-local.png": "地方",
        "https://static.cts.com.tw/news/images/icon-entertain.png": "娛樂",
        "https://static.cts.com.tw/news/images/icon-money.png": "財經",
        "https://static.cts.com.tw/news/images/icon-sports.png": "運動",
        "https://static.cts.com.tw/news/images/icon-weather.png": "氣象",
    }

    def read(self, start_from: datetime) -> Iterable[News]:
        try:
            metadatas = self._fetch_metadata()
            # return metadatas

        except Exception as e:
            self.logger.error(f'Stop crawling, because of {type(e).__name__}: "{e}"')

        if not metadatas or metadatas[0].publish_time < start_from:
            self.logger.info("Finish crawling.")
            return

        with ThreadPoolExecutor() as executor:
            metadatas = filter(lambda x: x.publish_time >= start_from, metadatas)

            future_to_url = {
                executor.submit(self._crawl_news, metadata): metadata
                for metadata in metadatas
            }
            for future in as_completed(future_to_url):
                try:
                    news = future.result()
                except Exception as e:
                    self.logger.error(
                        f'{future_to_url[future].url}: {type(e).__name__}: "{e}"'
                    )
                else:
                    yield news

    def _crawl_news(self, metadata: CtsNewsMetadata) -> News:
        response = requests.get(metadata.url, allow_redirects=False)
        response.raise_for_status()
        response.encoding = "utf-8"

        soup = bs4.BeautifulSoup(response.text, "html.parser")
        html = soup.select("div.news-artical")[0]
        if not html:
            raise ValueError("Article element not found.")

        title_elements = html.find("h1", {"class": "artical-title"})
        if not title_elements:
            raise ValueError("Title element not found.")

        title = title_elements.string.strip()
        content = soup.select("div.artical-content > p")
        content = list(map(lambda c: c.string.strip(), content))

        return News(
            title=title,
            content=content,
            content_hash=self.hash("".join(content)),
            category=metadata.category,
            modified_date=metadata.publish_time,
            media=self.media_name,
            tags=[metadata.category],
            url=metadata.url,
            url_hash=self.hash(metadata.url),
        )

    def _fetch_metadata(self) -> Iterable[CtsNewsMetadata]:
        response = requests.get(self.metadata_api, allow_redirects=False)
        response.raise_for_status()
        response.encoding = "utf-8"

        soup = bs4.BeautifulSoup(response.text, "html.parser")
        html = soup.select("div.newslist-container > a[href]")

        if not html:
            raise ValueError(f'Invalid response: {response}, missing "a" field.')

        parsed_news = list(map(self._parse_cts_api_response, html))
        return parsed_news

    def _parse_cts_api_response(self, html: bs4.element.Tag) -> CtsNewsMetadata:
        publish_time = parse(html.find("div", {"class": "newstime"}).string)
        category_url = html.find("div", {"class": "tag"}).img["src"]
        category = self.category_mapping.get(category_url, "未定義分類")
        url = html.attrs["href"]

        if not publish_time:
            raise ValueError("New's [publish time] is not found.")
        if not category_url:
            raise ValueError("New's [category] is not found.")
        if not url:
            raise ValueError("New's [url] is not found.")

        return CtsNewsMetadata(
            publish_time,
            category,
            url,
        )
