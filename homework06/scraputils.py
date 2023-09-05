import typing as tp
from pprint import pprint
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL: str = "https://news.ycombinator.com/"


def fetch_page_content(url: str) -> tp.Optional[str]:
    """Fetches the page content for a given URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException:
        return None


def extract_news(parser: BeautifulSoup) -> tp.List[tp.Dict[str, tp.Optional[tp.Union[str, int]]]]:
    """Extract news from a given web page"""
    news_list = []

    for athing in parser.find_all("tr", class_="athing"):
        subtext = athing.find_next("td", class_="subtext")
        title_data = athing.find_next("span", class_="titleline")

        if not subtext or not title_data or not title_data.a:
            continue

        hnuser = subtext.find("a", class_="hnuser")
        score = subtext.find("span", class_="score")
        all_links = subtext.find_all("a")

        author = hnuser.text if hnuser else None
        comments = all_links[-1].text.split()[0] if all_links else None
        points = score.text.split()[0] if score else None
        title = title_data.a.text
        url = title_data.a["href"]

        news_data = {
            "author": author,
            "comments": int(comments) if comments and comments.isdigit() else None,
            "points": int(points) if points and points.isdigit() else None,
            "title": title,
            "url": url if url.startswith("http") else "https://news.ycombinator.com/" + url,
        }
        news_list.append(news_data)

    return news_list


def extract_next_page(parser: BeautifulSoup) -> tp.Optional[str]:
    """Fetches the URL of the next page."""
    next_link = parser.find("a", class_="morelink")
    if next_link and "href" in next_link.attrs:
        return urljoin(BASE_URL, next_link["href"])
    return None


def get_news(url: str, n_pages: int = 1) -> tp.List[tp.Dict[str, tp.Optional[tp.Union[str, int]]]]:
    """Collect news from a given web page"""
    news = []
    for _ in range(n_pages):
        print(f"Collecting data from page: {url}")
        content = fetch_page_content(url)
        if not content:
            print(f"Failed to fetch content from {url}")
            break

        soup = BeautifulSoup(content, "html.parser")
        news.extend(extract_news(soup))

        next_page_url = extract_next_page(soup)
        if not next_page_url:
            break

        url = next_page_url

    return news
