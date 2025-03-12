from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from itertools import count

import bs4
import requests
from dateutil.parser import parse

from sync_crawler.crawlers.base_crawler import BaseCrawler
from sync_crawler.models.news import News


@dataclass
class EttodayNewsMetadata:
    publish_time: datetime
    category: str | None
    url: str


class EttodayCrawler(BaseCrawler):
    media_name = "ettoday"
    metadata_api = "https://www.ettoday.net"

    def read(self, start_from: datetime) -> Iterable[News]:
        for page in count(0, step=1):
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

    def _crawl_news(self, metadata: EttodayNewsMetadata) -> News:
        response = requests.get(
            metadata.url,
            allow_redirects=False,
        )
        response.raise_for_status()
        response.encoding = "utf-8"

        soup = bs4.BeautifulSoup(response.text, "html.parser")
        html = soup.select("div.story")

        if not html:
            raise ValueError("Article element not found.")

        title_element = soup.select("header > h1.title")
        if not title_element:
            title_element = soup.select("header > h1.title_article")
        if not title_element:
            raise ValueError("Title element not found.")
        title = title_element[0].string.strip()

        content = soup.select("div.story > p:not(:has(img))")
        content = [
            c.string.strip()
            for c in content
            if isinstance(c, bs4.element.Tag) and c.string
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

    def _fetch_metadata(self, page) -> Iterable[EttodayNewsMetadata]:
        response = None
        now = datetime.now()

        if page == 0:  # if page == 0 then request potal.
            response = requests.post(
                self.metadata_api
                + "/news/news-list-"
                + f"{now.year}-{now.month}-{now.day}"
                + "-0.htm",
                allow_redirects=False,
            )
        else:
            response = requests.post(
                self.metadata_api + "/show_roll.php",
                allow_redirects=False,
                data={
                    "offset": page,
                    "tPage": 3,
                    "tFile": now.strftime("%Y%M%D") + ".xml",
                    "tOt": 0,
                    "tSi": 100,
                    "tAr": 0,
                },
            )

        response.raise_for_status()
        response.encoding = "utf-8"
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        html = None
        if page == 0:
            html = soup.select("div.part_list_2 > h3")
        else:
            html = soup.select("h3")

        if not html:
            raise ValueError(f'Invalid response: {response}, missing "a" field.')

        parsed_news = list(map(self._parse_ettoday_api_response, html))
        return parsed_news

    def _parse_ettoday_api_response(self, html: bs4.element.Tag) -> EttodayNewsMetadata:
        publish_time = parse(html.find("span", {"class": "date"}).string)
        category = html.find("em", {"class": "tag"}).string
        url = html.a["href"]

        if not publish_time:
            raise ValueError("New's [publish time] is not found.")
        if not category:
            raise ValueError("New's [category] is not found.")
        if not url:
            raise ValueError("New's [url] is not found.")

        return EttodayNewsMetadata(
            publish_time,
            category,
            url,
        )
