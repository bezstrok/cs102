import csv
import string

from bayes import BayesSetup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


def clean(s: str) -> str:
    translator = str.maketrans("", "", string.punctuation)
    return s.translate(translator).lower()


if __name__ == "__main__":
    # Study code
    with open("data/SMSSpamCollection", encoding="utf8") as f:
        data = list(csv.reader(f, delimiter="\t"))

    X, y = [], []
    for target, msg in data:
        X.append(msg)
        y.append(target)
    X = list(map(clean, X))
    # Study code

    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=3900, shuffle=False)

    alpha: float = 0.05

    my_model = BayesSetup(alpha=alpha)
    sklearn_model = Pipeline(
        [("vectorizer", TfidfVectorizer()), ("classifier", MultinomialNB(alpha=alpha))]
    )

    my_model.fit(X_train, y_train)
    sklearn_model.fit(X_train, y_train)

    my_model_score = my_model.score(X_test, y_test)
    sklearn_model_score = sklearn_model.score(X_test, y_test)

    print(f"{my_model_score = }\n{sklearn_model_score = }")
    # my_model_score = 0.9838516746411483
    # sklearn_model_score = 0.9820574162679426
