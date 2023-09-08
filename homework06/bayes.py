import math
import string
import typing as tp
from collections import Counter, defaultdict

from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer


def clean(s: str) -> str:
    translator = str.maketrans("", "", string.punctuation)
    return s.translate(translator).lower()


class NaiveBayesClassifier:
    def __init__(self, alpha: float):
        self.alpha = alpha
        self.word_prob: tp.DefaultDict[int, tp.DefaultDict[str, float]] = defaultdict(
            lambda: defaultdict(float)
        )
        self.class_prob: tp.DefaultDict[str, float] = defaultdict(float)

    def fit(self, x: csr_matrix, y: tp.List[str]) -> None:
        total_docs = x.shape[0]

        class_counts: tp.Counter[str] = Counter(y)
        feature_counts: tp.DefaultDict[str, tp.Counter[int]] = defaultdict(Counter)

        # Calculate word counts per class
        for idx, label in enumerate(y):
            feature_indices = x[idx].indices
            for feature_idx in feature_indices:
                feature_counts[label][feature_idx] += 1

        # Calculate log probabilities for classes -> ln P(C=c)
        for label, count in class_counts.items():
            self.class_prob[label] = math.log(count / total_docs)

        # Calculate log probabilities for words given a class -> ln P(w_i|C=c)
        vocab_size = x.shape[1]
        for label in class_counts:
            total_word_counts = sum(feature_counts[label].values()) + self.alpha * vocab_size
            for feature_idx in range(vocab_size):
                self.word_prob[feature_idx][label] = math.log(
                    (feature_counts[label][feature_idx] + self.alpha) / total_word_counts
                )

    def get_label_prediction(self, x: csr_matrix) -> str:
        # Calculating log probabilities -> ln P(C=c) + sum_i ln P(w_i|C = c)
        label_probabilities = {}
        for label in self.class_prob:
            label_probabilities[label] = self.class_prob[label]
            feature_indices = x.indices
            for feature_idx in feature_indices:
                label_probabilities[label] += self.word_prob[feature_idx][label]

        # argmax_c
        return max(label_probabilities, key=label_probabilities.get)  # type: ignore

    def predict(self, x: csr_matrix) -> tp.List[str]:
        return [self.get_label_prediction(x[idx]) for idx in range(x.shape[0])]

    def score(self, x_test: csr_matrix, y_test: tp.List[str]) -> float:
        predictions = self.predict(x_test)
        return sum(p == y for p, y in zip(predictions, y_test)) / len(y_test)


class BayesSetup:
    def __init__(self, alpha: float, text_cleaner: tp.Callable = clean):
        self.vectorizer = TfidfVectorizer()
        self.classifier = NaiveBayesClassifier(alpha=alpha)
        self.text_cleaner = text_cleaner

    def fit(self, x: tp.List[str], y: tp.List[str]) -> None:
        x_transformed = self.vectorizer.fit_transform(map(clean, x))
        self.classifier.fit(x_transformed, y)

    def predict(self, x: tp.List[str]) -> tp.List[str]:
        x_transformed = self.vectorizer.transform(map(clean, x))
        return self.classifier.predict(x_transformed)

    def score(self, x_test: tp.List[str], y_test: tp.List[str]) -> float:
        x_transformed = self.vectorizer.transform(map(clean, x_test))
        return self.classifier.score(x_transformed, y_test)
