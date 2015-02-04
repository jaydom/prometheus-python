import unittest

from metricdict import MetricDict


class TestMetricDict(unittest.TestCase):

    def setUp(self):
        pass

    def test_bad_keys(self):
        with self.assertRaises(TypeError) as context:
            metrics = MetricDict()
            metrics['not_valid'] = "value"

        self.assertEqual('Only accepts dicts as keys', str(context.exception))

    def test_set(self):
        metrics = MetricDict()
        data = (
            ({'a': 1}, 1000),
            ({'b': 2, 'c': 3}, 2000),
            ({'d': 4, 'e': 5, 'f': 6}, 3000),
        )

        for i in data:
            metrics[i[0]] = i[1]

        self.assertEqual(len(data), len(metrics))

    def test_get(self):
        metrics = MetricDict()
        data = (
            ({'a': 1}, 1000),
            ({'b': 2, 'c': 3}, 2000),
            ({'d': 4, 'e': 5, 'f': 6}, 3000),
        )

        for i in data:
            metrics[i[0]] = i[1]

        for i in data:
            self.assertEqual(i[1], metrics[i[0]])

    def test_override(self):
        metrics = MetricDict()
        key = {'a': 1}

        for i in range(100):
            metrics[key] = i
            self.assertEqual(i, metrics[key])

        self.assertEqual(1, len(metrics))

    def test_similar(self):
        metrics = MetricDict()
        data = (
            ({'d': 4, 'e': 5, 'f': 6}, 3000),
            ({'e': 5, 'd': 4, 'f': 6}, 4000),
            ({'d': 4, 'f': 6, 'e': 5}, 5000),
        )

        for i in data:
            metrics[i[0]] = i[1]

        self.assertEqual(1, len(metrics))

    def test_all(self):
        metrics = MetricDict()
        data = (
            ({'d': 4, 'e': 5, 'f': 6}, 3000),
            ({'e': 5, 'd': 4, 'f': 6}, 4000),
            ({'d': 4, 'f': 6, 'e': 5}, 5000),
            ({'d': 41, 'f': 61, 'e': 51}, 6000),
            ({'d': 41, 'e': 51, 'f': 61}, 7000),
            ({'f': 61, 'e': 51, 'd': 41}, 8000),
        )

        for i in data:
            metrics[i[0]] = i[1]

        self.assertEqual(2, len(metrics))

        self.assertEqual(5000, metrics[{'d': 4, 'e': 5, 'f': 6}])
        self.assertEqual(8000, metrics[{'d': 41, 'f': 61, 'e': 51}])

if __name__ == '__main__':
    unittest.main()