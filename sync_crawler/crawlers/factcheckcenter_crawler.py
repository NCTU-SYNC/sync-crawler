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
class FactcheckcenterNewsMetadata:
    publish_time: datetime
    category: Optional[str]
    url: str


class FactcheckcenterCrawler(BaseCrawler):
    media_name = "factcheckcenter"
    metadata_api = "https://tfc-taiwan.org.tw"

    def read(self, start_from: datetime) -> Iterable[News]:
        for page in count(0, step=1):
            try:
                metadatas = self._fetch_metadata(page)

            except Exception as e:
                self.logger.error(
                    f'Stop crawling, because of {type(e).__name__}: "{e}"'
                )

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

    def _crawl_news(self, metadata: FactcheckcenterNewsMetadata) -> News:
        response = requests.get(self.metadata_api + metadata.url, allow_redirects=False)
        response.raise_for_status()
        response.encoding = "utf-8"

        soup = bs4.BeautifulSoup(response.text, "html.parser")
        html = soup.select("div.node-inner")[0]
        if not html:
            raise ValueError("Article element not found.")

        title_elements = html.find("h2", {"class": "node-title"})
        if not title_elements:
            raise ValueError("Title element not found.")

        title = title_elements.string.strip()
        content = soup.select("div.node-preface > p")  # preface
        content = content + soup.select(
            "div.field-item > h2,\
            div.field-item > p > span:not(:has(*)),\
            div.field-item > p:not(:has(*))"
        )
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

    def _fetch_metadata(self, page) -> Iterable[FactcheckcenterNewsMetadata]:
        response = requests.get(
            self.metadata_api + "/articles/report?page=" + str(page),
            allow_redirects=False,
        )
        response.raise_for_status()
        response.encoding = "utf-8"

        soup = bs4.BeautifulSoup(response.text, "html.parser")
        html = soup.select(
            "div.moscone-flipped-content div.view-content > div.views-row > div.views-row-inner"
        )

        if not html:
            raise ValueError(f'Invalid response: {response}, missing "a" field.')

        parsed_news = list(map(self._parse_factcheckcenter_api_response, html))
        return parsed_news

    def _parse_factcheckcenter_api_response(
        self, html: bs4.element.Tag
    ) -> FactcheckcenterNewsMetadata:
        publish_time = parse(
            html.find("div", {"class": "post-date"}).string.replace("發布日期：", "")
        )
        category = html.find("div", {"class": "attr-tag"}).a.string
        url = html.find("div", {"class": "entity-list-img"}).a["href"]

        if not publish_time:
            raise ValueError("New's [publish time] is not found.")
        if not category:
            raise ValueError("New's [category] is not found.")
        if not url:
            raise ValueError("New's [url] is not found.")

        return FactcheckcenterNewsMetadata(
            publish_time,
            category,
            url,
        )
