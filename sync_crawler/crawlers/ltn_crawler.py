from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from itertools import count

import bs4
import requests
from dateutil.parser import parse

from sync_crawler.crawlers.base_crawler import BaseCrawler, ignore_exception
from sync_crawler.models.news import News


@dataclass
class LtnNewsMetadata:
    publish_time: datetime
    category: str
    url: str


class LtnCrawler(BaseCrawler):
    media_name = "ltn"
    metadata_api = "https://news.ltn.com.tw/ajax/breakingnews/all/{}"

    def read(self, start_from: datetime) -> Iterable[News]:
        for page in count(1, step=1):
            try:
                metadatas = list(self._fetch_metadata(page))
            except Exception as e:
                self.logger.error(
                    f"Failed to fetch metadata from page {page}, because {e}"
                )
                break

            with ThreadPoolExecutor() as executor:
                news = executor.map(
                    self._crawl_news,
                    filter(lambda x: x.publish_time >= start_from, metadatas),
                )
                news = filter(lambda x: x is not None, news)

            yield from news

            if not metadatas or metadatas[-1].publish_time < start_from:
                break

    @ignore_exception
    def _crawl_news(self, metadata: LtnNewsMetadata) -> News:
        response = requests.get(metadata.url, allow_redirects=False)
        response.encoding = "utf-8"

        soup = bs4.BeautifulSoup(response.text, "html.parser")

        title = soup.select("[itemprop=articleBody] > h1")[0].text.strip()
        content = [
            tag.text.strip()
            for tag in soup.select(
                "[data-desc=內容頁] > p:not([class*=ir]):not([class*=app])"
            )
        ]

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

    def _fetch_metadata(self, page: int) -> Iterable[LtnNewsMetadata]:
        url = self.metadata_api.format(page)
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            self.logger.error(f"HTTP request failed: {e}")
            return []

        response = response.json()
        if "data" not in response:
            self.logger.error(f"Invalid response: {response}, missing 'data' field.")
            return []

        if isinstance(response["data"], list):
            responses = response["data"]
        elif isinstance(response["data"], dict):
            responses = response["data"].values()
        else:
            self.logger.error(
                f"Invalid response: {response}, expected 'data' to be list or dict, but got {type(response['data'])}."
            )
            return []

        try:
            parsed_news = map(self._parse_ltn_api_response, responses)
        except Exception as e:
            self.logger.error(f"Failed to parse response: {e}")
            return []

        return parsed_news

    def _parse_ltn_api_response(self, response: dict) -> LtnNewsMetadata:
        publish_time = parse(response["time"])

        return LtnNewsMetadata(
            publish_time=publish_time,
            category=response["tagText"],
            url=response["url"],
        )
