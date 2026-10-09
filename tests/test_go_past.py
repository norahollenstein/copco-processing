"""Regression tests for go-past time."""

import unittest
from itertools import product

import numpy as np

from helpers import get_go_past_times


class GoPastTest(unittest.TestCase):
    def test_regression_paths(self):
        for words, expected in (
            ([0, 1, 2], 100),
            ([1, 0, 1, 2], 300),
            ([1, 0, 2], 200),
            ([1, 1, 0, 1, 2], 400),
            ([1, 0, 1, 0, 1, 2], 500),
            ([1, 2, 1], 100),
            ([1, 0, 1], 300),
        ):
            with self.subTest(words=words):
                result = get_go_past_times([(word, 100) for word in words], 3)
                self.assertEqual(result[1], expected)

    def test_released_trial(self):
        # P01, trial 11: sikret -> havde -> sig.
        result = get_go_past_times([(1, 274), (0, 161), (2, 339)], 3)
        self.assertEqual(result[1], 435)

    def test_paper_figure_three(self):
        words = [1, 1, 1, 0, 0, 1, 2, 2, 2, 1]
        result = get_go_past_times([(word, 100) for word in words], 3)
        self.assertEqual(result[1], 600)

    def test_unfixated_words(self):
        np.testing.assert_equal(get_go_past_times([], 3), [np.nan] * 3)
        np.testing.assert_equal(get_go_past_times([(1, 125)], 3), [np.nan, 125, np.nan])

    def test_first_visit_during_regression(self):
        result = get_go_past_times([(2, 100), (1, 150), (0, 200), (2, 250)], 3)
        self.assertEqual(result[1], 350)

    def test_short_sequences(self):
        for length in range(1, 7):
            for words in product(range(3), repeat=length):
                with self.subTest(words=words):
                    durations = [100 + 10 * i for i in range(length)]
                    result = get_go_past_times(list(zip(words, durations)), 3)
                    for word in range(3):
                        if word not in words:
                            self.assertTrue(np.isnan(result[word]))
                            continue
                        start = words.index(word)
                        exits = [i for i in range(start + 1, length) if words[i] > word]
                        end = min(exits) if exits else length
                        self.assertEqual(result[word], sum(durations[start:end]))


if __name__ == '__main__':
    unittest.main()
