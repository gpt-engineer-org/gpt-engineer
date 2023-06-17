import unittest
import os
from gpt_engineer.db import DB


class TestDB(unittest.TestCase):
    def setUp(self):
        # setup: use /tmp for testing
        self.path = '/tmp/test_db'
        self.db = DB(self.path)

    def test_db_operations(self):
        self.db['test'] = 'test'
        self.assertEqual(self.db['test'], 'test')
        self.db['test'] = 'test2'
        self.assertEqual(self.db['test'], 'test2')
        self.db['test2'] = 'test2'
        self.assertEqual(self.db['test2'], 'test2')
        self.assertEqual(self.db['test'], 'test2')

    def test_non_existent_key(self):
        with self.assertRaises(KeyError):
            self.db['non_existent_key']

    def test_different_data_types(self):
        self.db['int_value'] = 123
        self.assertEqual(self.db['int_value'], '123')
        self.db['bool_value'] = True
        self.assertEqual(self.db['bool_value'], 'True')

    def tearDown(self):
        # teardown: clean up files created during test
        for file in ['test', 'test2', 'int_value', 'bool_value']:
            try:
                os.remove(self.path + '/' + file)
            except FileNotFoundError:
                pass