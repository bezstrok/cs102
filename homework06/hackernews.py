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
    model = BayesSetup(alpha=1.0)

    with session() as s:
        training_data = s.query(News).filter(News.label.isnot(None)).all()

        if not training_data:
            redirect("/news")

        X_train = [news.title for news in training_data]
        y_train = [news.label for news in training_data]
        model.fit(X_train, y_train)

        unclassified_data = s.query(News).filter_by(label=None).all()
        X_predict = [news.title for news in unclassified_data]
        predicted_labels = model.predict(X_predict)

        label_order = {"good": 2, "maybe": 1, "never": 0}
        sorted_news = [
            {
                "url": news.url,
                "title": news.title,
                "author": news.author,
                "points": news.points,
                "comments": news.comments,
                "label": predicted_label,
            }
            for news, predicted_label in sorted(
                zip(unclassified_data, predicted_labels),
                key=lambda x: label_order[x[1]],
                reverse=True,
            )
        ]

        return template("personalized_news", rows=sorted_news)


if __name__ == "__main__":
    run(host="localhost", port=8080)
