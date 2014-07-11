# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest


from presence_analyzer import main, utils


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)

TEST_DATA_XML = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.xml'
)


# pylint: disable=E1103
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        main.app.config.update({'DATA_XML': TEST_DATA_XML})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday.html')

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        #self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {
            u'user_id': 10,
            u'name': u'Maciej Z.',
            u'avatar': 'https://intranet.stxnext.pl:443/api/images/users/10',
        })

    def test_mean_time_weekday_view(self):
        """
        Test mean time weekday view.
        """
        resp = self.client.get('/api/v1/mean_time_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)

        resp = self.client.get('/api/v1/mean_time_weekday/2')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 0)

    def test_presence_weekday_view(self):
        """
        Test presence weekday view.
        """
        resp = self.client.get('/api/v1/presence_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')

        resp = self.client.get('/api/v1/presence_weekday/2')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 0)

    def test_start_end_view(self):
        """
        Test start/end view.
        """
        resp = self.client.get('/api/v1/presence_start_end_view/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)

        resp = self.client.get('/api/v1/presence_start_end_view/2')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 0)

    def test_render_mean_time(self):
        """
        Test if template are rendered properly.
        """
        resp = self.client.get('/mean_time_weekday.html')
        self.assertEqual(resp.status_code, 200)

    def test_render_start_end(self):
        """
        Test if template are rendered properly.
        """
        resp = self.client.get('/presence_start_end.html')
        self.assertEquals(resp.status_code, 200)

    def test_render_weekday(self):
        """
        Test if template are rendered properly.
        """
        resp = self.client.get('/presence_weekday.html')
        self.assertEqual(resp.status_code, 200)


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        main.app.config.update({'DATA_XML': TEST_DATA_XML})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(data[10][sample_date]['start'],
                         datetime.time(9, 39, 5))

    def test_group_by_weekday(self):
        """
        Test if function is grouping by weekdays.
        """
        data = utils.get_data()
        expected = {
            0: [],
            1: [30047],
            2: [24465],
            3: [23705],
            4: [],
            5: [],
            6: [],
        }
        expected_2 = {
            0: [24123],
            1: [16564],
            2: [25321],
            3: [22969, 22999],
            4: [6426],
            5: [],
            6: [],
        }
        self.assertDictEqual(utils.group_by_weekday(data[10]), expected)
        self.assertDictEqual(utils.group_by_weekday(data[11]), expected_2)

    def test_interval(self):
        """
        Test interval calculations.
        """
        # start_time == 0
        start_time = datetime.time(0, 0, 0)
        end_time = datetime.time(1, 10, 20)
        self.assertEqual(utils.interval(start_time, end_time), 4220)

        # start_time != 0
        start_time = datetime.time(1, 10, 20)
        end_time = datetime.time(2, 20, 20)
        self.assertEqual(utils.interval(start_time, end_time), 4200)

        start_time = datetime.time(0, 0, 0)
        end_time = datetime.time(23, 59, 59)
        self.assertEqual(utils.interval(start_time, end_time), 86399)

        start_time = datetime.time(0, 0, 0)
        end_time = datetime.time(0, 0, 0)
        self.assertEqual(utils.interval(start_time, end_time), 0)

    def test_mean(self):
        """
        Test calculations of arithmetic mean.
        """
        self.assertEqual(utils.mean([]), 0)
        self.assertEqual(utils.mean(range(1, 10)), 5.0)
        self.assertEqual(utils.mean(range(1, 3)), 1.5)
        self.assertIsInstance(utils.mean(range(1, 5)), float)
        self.assertIsInstance(utils.mean([1]), float)

    def test_seconds_since_midnight(self):
        """
        Test calculations of seconds.
        """
        time = datetime.time(1, 0, 20)
        seconds = utils.seconds_since_midnight(time)
        self.assertEqual(seconds, 3620)

        time = datetime.time(0, 0, 0)
        seconds = utils.seconds_since_midnight(time)
        self.assertEqual(seconds, 0)

        time = datetime.time(23, 59, 59)
        seconds = utils.seconds_since_midnight(time)
        self.assertEqual(seconds, 86399)

    def test_start_end_presence(self):
        """
        Test calculations of start/end presence.
        """
        data = utils.get_data()
        expected = {
            0: {'start': [], 'end': []},
            1: {'start': [34745], 'end': [64792]},
            2: {'start': [33592], 'end': [58057]},
            3: {'start': [38926], 'end': [62631]},
            4: {'start': [], 'end': []},
            5: {'start': [], 'end': []},
            6: {'start': [], 'end': []},
        }
        expected_2 = {
            0: {'start': [33134], 'end': [57257]},
            1: {'start': [33590], 'end': [50154]},
            2: {'start': [33206], 'end': [58527]},
            3: {'start': [37116, 34088], 'end': [60085, 57087]},
            4: {'start': [47816], 'end': [54242]},
            5: {'start': [], 'end': []},
            6: {'start': [], 'end': []},
        }
        self.assertDictEqual(utils.start_end_presence(data[10]), expected)
        self.assertDictEqual(utils.start_end_presence(data[11]), expected_2)


def suite():
    """
    Default test suite.
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return suite


if __name__ == '__main__':
    unittest.main()
