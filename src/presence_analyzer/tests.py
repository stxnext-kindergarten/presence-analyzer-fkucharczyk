# -*- coding: utf-8 -*-
"""Presence analyzer unit tests."""
import os.path
import json
import datetime
import unittest

import main
import views
import utils


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)


class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """Views tests."""

    def setUp(self):
        """Before each test, set up a environment."""
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        self.client = main.app.test_client()

    def tearDown(self):
        """Get rid of unused objects after each test."""
        pass

    def test_mainpage(self):
        """Test main page redirect."""
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday.html')

    def test_api_users(self):
        """Test users listing."""
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {u'user_id': 10, u'name': u'User 10'})

    def test_mean_time_weekday_view(self):
        """Test mean presence time of given user grouped by weekday."""
        resp_user_not_found = self.client.get('/api/v1/mean_time_weekday/0')
        self.assertEqual(resp_user_not_found.status_code, 404)
        resp = self.client.get('/api/v1/mean_time_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        proper_data = [
            ['Mon', 0],
            ['Tue', 30047.0],
            ['Wed', 24465.0],
            ['Thu', 23705.0],
            ['Fri', 0],
            ['Sat', 0],
            ['Sun', 0],
        ]
        self.assertEqual(data, proper_data)

    def test_presence_weekday_view(self):
        """Test total presence time of given user grouped by weekday."""
        resp_404 = self.client.get('/api/v1/presence_weekday/0')
        self.assertEqual(resp_404.status_code, 404)
        resp = self.client.get('/api/v1/presence_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        proper_data = [
            ['Weekday', 'Presence (s)'],
            ['Mon', 0],
            ['Tue', 30047],
            ['Wed', 24465],
            ['Thu', 23705],
            ['Fri', 0],
            ['Sat', 0],
            ['Sun', 0],
        ]
        self.assertEqual(data, proper_data)


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """Utility functions tests."""

    def setUp(self):
        """Before each test, set up a environment."""
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})

    def tearDown(self):
        """Get rid of unused objects after each test."""
        pass

    def test_get_data(self):
        """Test parsing of CSV file."""
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(
            data[10][sample_date]['start'],
            datetime.time(9, 39, 5)
        )

    def test_seconds_since_midnight(self):
        """Test calculating the amount of seconds since midnight."""
        self.assertEqual(
            0, utils.seconds_since_midnight(datetime.time(0, 0, 0)),
        )
        self.assertEqual(
            10,
            utils.seconds_since_midnight(datetime.time(0, 0, 10)),
        )
        self.assertEqual(
            3600,
            utils.seconds_since_midnight(datetime.time(1, 0, 0)),
        )
        self.assertEqual(
            3661,
            utils.seconds_since_midnight(datetime.time(1, 1, 1)),
        )

    def test_group_by_weekday(self):
        """Test groups presence entries by weekday."""
        data = utils.get_data()
        proper_data =[[], [30047], [24465], [23705], [], [], []]
        self.assertEqual(utils.group_by_weekday(data[10]), proper_data)

    def test_interval(self):
        """Test calculation of interval in seconds between
        two datetime.time objects.
        """
        self.assertEqual(
            0, utils.interval(datetime.time(0, 0, 0),datetime.time(0, 0, 0)),
        )
        self.assertEqual(
            1, utils.interval(datetime.time(0, 0, 1),datetime.time(0, 0, 2)),
        )

    def test_mean(self):
        """Test calculation of arithmetic mean"""
        self.assertEqual(
            0, utils.mean([])
        )
        self.assertEqual(
            2, utils.mean([1,2,3])
        )
        self.assertEqual(
            0, utils.mean([0, 0, 0])
        )

def suite():
    """Default test suite."""
    base_suite = unittest.TestSuite()
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return base_suite


if __name__ == '__main__':
    unittest.main()
