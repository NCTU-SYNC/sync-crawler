import re
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timedelta
from itertools import count
from typing import Optional

import bs4
import requests
from dateutil.parser import parse

from sync_crawler.crawlers.base_crawler import BaseCrawler
from sync_crawler.models.news import News


@dataclass
class EbcNewsMetadata:
    publish_time: datetime
    category: Optional[str]
    url: str


class EbcCrawler(BaseCrawler):
    media_name = "ebc"
    metadata_api = "https://news.ebc.net.tw"

    def read(self, start_from: datetime) -> Iterable[News]:
        for page in count(1, step=1):
            try:
                metadatas = self._fetch_metadata(page)

            except Exception as e:
                self.logger.error(
                    f'Stop crawling, because of {type(e).__name__}: "{e}"'
                )

            if (
                not isinstance(metadatas, list)
                or metadatas[0].publish_time < start_from
            ):
                self.logger.info("Finish crawling.")
                return

            print(self._crawl_news(metadatas[0]))

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

    def _crawl_news(self, metadata: EbcNewsMetadata) -> News:
        response = requests.get(
            metadata.url,
            headers={
                "User-Agent": "",
            },
            allow_redirects=False,
        )
        response.raise_for_status()
        response.encoding = "utf-8"

        soup = bs4.BeautifulSoup(response.text, "html.parser")
        html = soup.select("div.article_box")

        if not html:
            raise ValueError("Article element not found.")

        title_element = soup.select("div.article_header > h1")[0]
        if not title_element:
            raise ValueError("Title element not found.")
        title = title_element.string.strip()

        category_element = soup.select(
            "div.article_box div.breadcrumb div:last-child > a"
        )[0]
        if not category_element:
            raise ValueError("Category element not found.")
        category = category_element.string.strip()

        content = soup.select("div.article_container div.article_content > p")
        content = [
            c.string.strip()
            for c in content
            if isinstance(c, bs4.element.Tag) and c.string
        ]

        return News(
            title=title,
            content=content,
            content_hash=self.hash("".join(content)),
            category=category,
            modified_date=metadata.publish_time,
            media=self.media_name,
            tags=[category],
            url=metadata.url,
            url_hash=self.hash(metadata.url),
        )

    def _fetch_metadata(self, page) -> Iterable[EbcNewsMetadata]:
        response = requests.post(
            self.metadata_api + "/list/load",
            files={
                "list_type": (None, "realtime"),
                "cate_code": (None, ""),
                "page": (None, page),
            },
            headers={"User-Agent": "", "x-requested-with": "XMLHttpRequest"},
            allow_redirects=False,
        )

        response.raise_for_status()
        response.encoding = "utf-8"
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        html = soup.select("div.list.m_group > a.item.row_box")

        if not html:
            raise ValueError(f'Invalid response: {response}, missing "a" field.')

        parsed_news = list(map(self._parse_ebc_api_response, html))
        return parsed_news

    def _parse_ebc_api_response(self, html: bs4.element.Tag) -> EbcNewsMetadata:
        publish_time_str = self._convert_time_format(
            html.find("div", {"class": "item_time"}).string
        )
        publish_time = parse(publish_time_str)
        category = "null"
        url = html.attrs["href"]

        if not publish_time:
            raise ValueError("New's [publish time] is not found.")
        if not category:
            raise ValueError("New's [category] is not found.")
        if not url:
            raise ValueError("New's [url] is not found.")

        return EbcNewsMetadata(
            publish_time,
            category,
            url=(self.metadata_api + url),
        )

    def _convert_time_format(self, time_str):
        now = datetime.now()

        if "分鐘前" in time_str:
            minutes = int(re.search(r"\d+", time_str).group())
            return (now - timedelta(minutes=minutes)).strftime("%Y-%m-%d")
        elif "小時前" in time_str:
            hours = int(re.search(r"\d+", time_str).group())
            return (now - timedelta(hours=hours)).strftime("%Y-%m-%d")
        elif "天前" in time_str:
            days = int(re.search(r"\d+", time_str).group())
            return (now - timedelta(days=days)).strftime("%Y-%m-%d")
        else:
            month_day = datetime.strptime(time_str, "%m-%d %H:%M")
            year = now.year
            if now.month > month_day.month or (
                now.month == month_day.month and now.day > month_day.day
            ):
                year += 1
            return month_day.replace(year=now.year).strftime("%Y-%m-%d")
