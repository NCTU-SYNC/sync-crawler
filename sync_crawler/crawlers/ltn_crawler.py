from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from itertools import count
from typing import Optional

import bs4
import requests
from dateutil.parser import parse

from sync_crawler.crawlers.base_crawler import BaseCrawler
from sync_crawler.models.news import News


@dataclass
class LtnNewsMetadata:
    publish_time: datetime
    category: Optional[str]
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
                    f'Stop crawling, because of {type(e).__name__}: "{e}"'
                )
                break

            if not metadatas or metadatas[0].publish_time < start_from:
                self.logger.info("Finish crawling.")
                break

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

    def _crawl_news(self, metadata: LtnNewsMetadata) -> News:
        response = requests.get(metadata.url, allow_redirects=False)
        response.raise_for_status()
        response.encoding = "utf-8"

        soup = bs4.BeautifulSoup(response.text, "html.parser")

        title_elements = soup.select("[itemprop=articleBody] > h1")
        if not title_elements:
            raise ValueError("Title element not found.")
        title = title_elements[0].text.strip()
        content = [
            tag.text.strip()
            for tag in soup.select(
                "[data-desc=內容頁] > p:not([class*=ir]):not([class*=app])"
            )
        ]

        if metadata.category is None:
            raise ValueError(f"Cannot find category in {metadata.url}")

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
        response = requests.get(url)
        response.raise_for_status()
        response = response.json()

        if "data" not in response:
            raise ValueError(f"Invalid response: {response}, missing 'data' field.")

        if isinstance(response["data"], list):
            responses = response["data"]
        elif isinstance(response["data"], dict):
            responses = response["data"].values()
        else:
            raise ValueError(
                f"Invalid response: {response}, expected 'data' to be list or dict, but got {type(response['data'])}."
            )

        parsed_news = list(map(self._parse_ltn_api_response, responses))
        return parsed_news

    def _parse_ltn_api_response(self, response: dict) -> LtnNewsMetadata:
        publish_time = parse(response["time"])

        return LtnNewsMetadata(
            publish_time=publish_time,
            category=response["tagText"],
            url=response["url"],
        )
