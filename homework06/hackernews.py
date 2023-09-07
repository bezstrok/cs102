from bottle import redirect, request, route, run, template

from bayes import BayesSetup
from db import News, session
from scraputils import NEWEST_URL, get_news


@route("/")
@route("/news")
def news_list():
    with session() as s:
        rows = s.query(News).filter_by(label=None).all()
        return template("news_template", rows=rows)


@route("/add_label/")
def add_label():
    label_value = request.query.label
    news_id = request.query.id

    if not label_value or not news_id:
        redirect("/news")
        return

    with session() as s:
        news_item = s.query(News).filter_by(id=news_id).one()
        news_item.label = label_value
        s.commit()

    redirect("/news")


@route("/update")
def update_news():
    new_news_generator = get_news(NEWEST_URL, 1)

    for news_item in new_news_generator:
        with session() as s:
            is_exist = bool(
                s.query(News)
                .filter_by(title=news_item["title"], author=news_item["author"])
                .first()
            )

            if not is_exist:
                new_news = News(**news_item)
                s.add(new_news)
                s.commit()

    redirect("/news")


@route("/classify")
def classify_news():
    ...


if __name__ == "__main__":
    run(host="localhost", port=8080)
