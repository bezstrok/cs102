import math
import typing as tp
from collections import Counter, defaultdict

from scipy.sparse import csr_matrix


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
