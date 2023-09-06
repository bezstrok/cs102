from bottle import redirect, request, route, run, template

from bayes import NaiveBayesClassifier
from db import News, session
from dbutils import session_scope
from scraputils import NEWEST_URL, get_news


@route("/")
@route("/news")
def news_list():
    with session_scope() as s:
        rows = s.query(News).filter(News.label == None).all()
        return template("news_template", rows=rows)


@route("/add_label/")
def add_label():
    label_value = request.query.label
    news_id = request.query.id

    if not label_value or not news_id:
        redirect("/news")
        return

    with session_scope() as s:
        news_item = s.query(News).filter_by(id=news_id).one()
        news_item.label = label_value

    redirect("/news")


@route("/update")
def update_news():
    new_news_generator = get_news(NEWEST_URL, 1)

    for news_item in new_news_generator:
        with session_scope() as s:
            is_exist = bool(
                s.query(News)
                .filter_by(title=news_item["title"], author=news_item["author"])
                .first()
            )

            if not is_exist:
                new_news = News(
                    title=news_item["title"],
                    author=news_item["author"],
                    url=news_item["url"],
                    comments=news_item["comments"],
                    points=news_item["points"],
                )
                s.add(new_news)

    redirect("/news")


@route("/classify")
def classify_news():
    ...


if __name__ == "__main__":
    run(host="localhost", port=8080)
