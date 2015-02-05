import unittest

from collectors import Collector, Counter, Gauge


class TestCollectorDict(unittest.TestCase):

    def setUp(self):
        self.data = {
            'name': "logged_users_total",
            'help_text': "Logged users in the application",
            'const_labels': {"app": "my_app"},
        }

        self.c = Collector(**self.data)

    def test_initialization(self):
        self.assertEqual(self.data['name'], self.c.name)
        self.assertEqual(self.data['help_text'], self.c.help_text)
        self.assertEqual(self.data['const_labels'], self.c.const_labels)

    def test_set_value(self):
        data = (
            ({'country': "sp", "device": "desktop"}, 520),
            ({'country': "us", "device": "mobile"}, 654),
            ({'country': "uk", "device": "desktop"}, 1001),
            ({'country': "de", "device": "desktop"}, 995),
        )

        for m in data:
            self.c.set_value(m[0], m[1])

        self.assertEqual(len(data), len(self.c.values))

    def test_same_value(self):
        data = (
            ({'country': "sp", "device": "desktop", "ts": "GMT+1"}, 520),
            ({"ts": "GMT+1", 'country': "sp", "device": "desktop"}, 521),
            ({'country': "sp", "ts": "GMT+1", "device": "desktop"}, 522),
            ({"device": "desktop", "ts": "GMT+1", 'country': "sp"}, 523),
        )

        for m in data:
            self.c.set_value(m[0], m[1])

        self.assertEqual(1, len(self.c.values))
        self.assertEqual(523, self.c.values[data[0][0]])

    def test_get_value(self):
        data = (
            ({'country': "sp", "device": "desktop"}, 520),
            ({'country': "us", "device": "mobile"}, 654),
            ({'country': "uk", "device": "desktop"}, 1001),
            ({'country': "de", "device": "desktop"}, 995),
        )

        for m in data:
            self.c.set_value(m[0], m[1])

        for m in data:
            self.assertEqual(m[1], self.c.get_value(m[0]))

     #def test_set_value_mutex(self):
     #   # TODO: Check mutex
     #   pass

    def test_wrong_labels(self):

        # Normal set
        with self.assertRaises(ValueError) as context:
            self.c.set_value({'job': 1, 'ok': 2}, 1)

        self.assertEqual('Labels not correct', str(context.exception))

        with self.assertRaises(ValueError) as context:
            self.c.set_value({'__not_ok': 1, 'ok': 2}, 1)

        self.assertEqual('Labels not correct', str(context.exception))

        # Constructor set
        with self.assertRaises(ValueError) as context:
            Collector("x", "y", {'job': 1, 'ok': 2})

        self.assertEqual('Labels not correct', str(context.exception))

        with self.assertRaises(ValueError) as context:
            Collector("x", "y", {'__not_ok': 1, 'ok': 2})

        self.assertEqual('Labels not correct', str(context.exception))

    def test_get_all(self):
        data = (
            ({'country': "sp", "device": "desktop"}, 520),
            ({'country': "us", "device": "mobile"}, 654),
            ({'country': "uk", "device": "desktop"}, 1001),
            ({'country': "de", "device": "desktop"}, 995),
            ({'country': "zh", "device": "desktop"}, 520),
            ({'country': "ch", "device": "mobile"}, 654),
            ({'country': "ca", "device": "desktop"}, 1001),
            ({'country': "jp", "device": "desktop"}, 995),
            ({'country': "au", "device": "desktop"}, 520),
            ({'country': "py", "device": "mobile"}, 654),
            ({'country': "ar", "device": "desktop"}, 1001),
            ({'country': "pt", "device": "desktop"}, 995),
        )

        for i in data:
            self.c.set_value(i[0], i[1])

        sort_fn = lambda x: x[0]['country']
        sorted_data = sorted(data, key=sort_fn)
        sorted_result = sorted(self.c.get_all(), key=sort_fn)
        self.assertEqual(sorted_data, sorted_result)


class TestCounter(unittest.TestCase):

    def setUp(self):
        self.data = {
            'name': "logged_users_total",
            'help_text': "Logged users in the application",
            'const_labels': {"app": "my_app"},
        }

        self.c = Counter(**self.data)

    def test_set(self):

        data = (
            {
                'labels': {'country': "sp", "device": "desktop"},
                'values': range(10)
            },
            {
                'labels': {'country': "us", "device": "mobile"},
                'values': range(10, 20)
            },
            {
                'labels': {'country': "uk", "device": "desktop"},
                'values': range(20, 30)
            }
        )

        for i in data:
            for j in i['values']:
                self.c.set(i['labels'], j)

        self.assertEqual(len(data), len(self.c.values))

    def test_get(self):
        data = (
            {
                'labels': {'country': "sp", "device": "desktop"},
                'values': range(10)
            },
            {
                'labels': {'country': "us", "device": "mobile"},
                'values': range(10, 20)
            },
            {
                'labels': {'country': "uk", "device": "desktop"},
                'values': range(20, 30)
            }
        )

        for i in data:
            for j in i['values']:
                self.c.set(i['labels'], j)
                self.assertEqual(j, self.c.get(i['labels']))

        # Last check
        for i in data:
            self.assertEqual(max(i['values']), self.c.get(i['labels']))

    def test_inc(self):
        iterations = 100
        labels = {'country': "sp", "device": "desktop"}

        for i in range(iterations):
            self.c.inc(labels)

        self.assertEqual(iterations, self.c.get(labels))

    def test_add(self):
        labels = {'country': "sp", "device": "desktop"}
        iterations = 100

        for i in range(iterations):
            self.c.add(labels, i)

        self.assertEqual(sum(range(iterations)), self.c.get(labels))

    def test_negative_add(self):
        labels = {'country': "sp", "device": "desktop"}

        with self.assertRaises(ValueError) as context:
            self.c.add(labels, -1)
        self.assertEqual('Counters can\'t decrease', str(context.exception))


class TestGauge(unittest.TestCase):

    def setUp(self):
        self.data = {
            'name': "hdd_disk_used",
            'help_text': "Disk space used",
            'const_labels': {"server": "1.db.production.my-app"},
        }

        self.g = Gauge(**self.data)

    def test_set(self):
        data = (
            {
                'labels': {'max': "500G", 'dev': "sda"},
                'values': range(0, 500, 50)
            },
            {
                'labels': {'max': "1T", 'dev': "sdb"},
                'values': range(0, 1000, 100)
            },
            {
                'labels': {'max': "10T", 'dev': "sdc"},
                'values': range(0, 10000, 1000)
            }
        )

        for i in data:
            for j in i['values']:
                self.g.set(i['labels'], j)

        self.assertEqual(len(data), len(self.g.values))

    def test_get(self):
        data = (
            {
                'labels': {'max': "500G", 'dev': "sda"},
                'values': range(0, 500, 50)
            },
            {
                'labels': {'max': "1T", 'dev': "sdb"},
                'values': range(0, 1000, 100)
            },
            {
                'labels': {'max': "10T", 'dev': "sdc"},
                'values': range(0, 10000, 1000)
            }
        )

        for i in data:
            for j in i['values']:
                self.g.set(i['labels'], j)
                self.assertEqual(j, self.g.get(i['labels']))

        for i in data:
            self.assertEqual(max(i['values']), self.g.get(i['labels']))

    def test_inc(self):
        iterations = 100
        labels = {'max': "10T", 'dev': "sdc"}

        for i in range(iterations):
            self.g.inc(labels)
            self.assertEqual(i+1, self.g.get(labels))

        self.assertEqual(iterations, self.g.get(labels))

    def test_dec(self):
        iterations = 100
        labels = {'max': "10T", 'dev': "sdc"}
        self.g.set(labels, iterations)

        for i in range(iterations):
            self.g.dec(labels)
            self.assertEqual(iterations-(i+1), self.g.get(labels))

        self.assertEqual(0, self.g.get(labels))

    def test_add(self):
        iterations = 100
        labels = {'max': "10T", 'dev': "sdc"}

        for i in range(iterations):
            self.g.add(labels, i)

        self.assertEqual(sum(range(iterations)), self.g.get(labels))

    def test_add_negative(self):
        iterations = 100
        labels = {'max': "10T", 'dev': "sdc"}

        for i in range(iterations):
            self.g.add(labels, -i)

        self.assertEqual(sum(map(lambda x: -x, range(iterations))),
                         self.g.get(labels))

    def test_sub(self):
        iterations = 100
        labels = {'max': "10T", 'dev': "sdc"}

        for i in range(iterations):
            self.g.sub(labels, i)

        self.assertEqual(sum(map(lambda x: -x, range(iterations))),
                         self.g.get(labels))

    def test_sub_positive(self):
        iterations = 100
        labels = {'max': "10T", 'dev': "sdc"}

        for i in range(iterations):
            self.g.sub(labels, -i)

        self.assertEqual(sum(range(iterations)), self.g.get(labels))
