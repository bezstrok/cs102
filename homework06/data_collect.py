import argparse

from db import News, session
from scraputils import get_news

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Парсинг статей hackernews")
    parser.add_argument("url", type=str, help="Стартовая страница")
    parser.add_argument("--pages", type=int, default=1, help="Количество страниц")

    args = parser.parse_args()

    if args.pages <= 0:
        print("Количество страниц должно быть положительным числом.")
        exit(1)

    news_generator = get_news(args.url, args.pages)

    with session() as s:
        for news_item in news_generator:
            s.add(News(**news_item))
            s.commit()
