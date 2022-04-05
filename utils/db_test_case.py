import os
from pathlib import Path
from unittest import TestCase, mock

from utils import database

DB_PATH = Path.joinpath(Path(__file__).parent, 'app_test.db')


class DbTestCase(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """Initialize test db"""
        cnx_str_patcher = mock.patch('utils.database.get_cnx_str_uri', return_value=f'sqlite:///{DB_PATH}')
        cnx_str_patcher.start()

        database.init_db()

        cnx_str_patcher.stop()

    @classmethod
    def tearDownClass(cls) -> None:
        """Delete test db"""
        database.session.close_all()
        os.remove(DB_PATH)
