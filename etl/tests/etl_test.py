import os
from pathlib import Path
from unittest import mock, TestCase
from bs4 import BeautifulSoup

from utils import database
from utils.models.forward_rate import ForwardRate
from utils.models.forward_rate_run_batch import ForwardRateRunBatch
from etls.pensford_forward_rate_etl import PensfordForwardRateEtl

sample_tbl_html = """
<table class="table table-striped border-0" id="curve-table" style="height: 4875.99px; width: 797px;">
    <thead class="row-2 even sticky-top">
        <tr class="top-row-text" style="height: 73.9931px;">
            <td class="column-1" style="height: 74px; width: 168px; text-align: left;">
                <pre><span style="color: #000000;"><strong>Reset Date</strong></span></pre>
            </td>
            <td class="column-1" style="height: 74px; width: 202px; text-align: left;">
                <pre><span style="color: #000000;"><strong>1-month LIBOR</strong></span></pre>
            </td>
            <td class="column-1" style="height: 74px; width: 203px; text-align: left;">
                <pre><span style="color: #000000;"><strong>3-month LIBOR</strong></span></pre>
            </td>
            <td class="column-1" style="height: 74px; width: 224px; text-align: left;">
                <pre><span style="color: #000000;"><strong>1-month Term SOFR</strong></span></pre>
            </td>
        </tr>
    </thead>
    <tbody class="row-hover">
        <tr>
            <td style="width: 168px; padding: 4px;" width="93">3/28/2022</td>
            <td style="width: 202px; padding: 4px;" width="180">0.45743%</td>
            <td style="width: 203px; padding: 4px;" width="180">1.00600%</td>
            <td style="width: 224px; padding: 4px;" width="180">0.31258%</td>
        </tr>
        <tr>
            <td style="width: 168px; padding: 4px;">4/28/2022</td>
            <td style="width: 202px; padding: 4px;">0.91819%</td>
            <td style="width: 203px; padding: 4px;">1.26105%</td>
            <td style="width: 224px; padding: 4px;">0.68192%</td>
        </tr>
    </tbody>
</table>
"""

DB_PATH = Path.joinpath(Path(__file__).parent, 'app_test.db')


class EtlTest(TestCase):
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

    def setUp(self) -> None:
        self.tbl_soup = BeautifulSoup(sample_tbl_html, 'html.parser')
        self.etl = PensfordForwardRateEtl()

        self.fetch_rates_patcher = mock.patch(
            'etls.pensford_forward_rate_etl.PensfordForwardRateEtl._fetch_rates_page',
            return_value=self.tbl_soup
        )
        self.fetch_rates_patcher.start()

    def tearDown(self) -> None:
        self.fetch_rates_patcher.stop()

    def cols_idx_map_test(self):
        """Assert that headers are correctly mapped to col idx regardless of ordering"""
        target_cols = ('1-month LIBOR', 'Reset Date', '1-month Term SOFR')
        cols_idx_map = self.etl._find_tbl_head_idx(self.tbl_soup, target_cols)

        expected = {
            '1-month LIBOR': 1,
            'Reset Date': 0,
            '1-month Term SOFR': 3
        }

        self.assertDictEqual(cols_idx_map, expected)

    def yield_rates_test(self):
        """Assert a row is yielded in the given order"""
        row = next(self.etl._yield_rates(self.tbl_soup))
        expected = ['3/28/2022', '0.45743%', '1.00600%', '0.31258%']

        self.assertListEqual(row, expected)

    def clean_rate_test(self):
        """Assert a string from Pensford is accurately cast to a float"""
        cleaned_rate = self.etl._clean_rate('1.00600%')
        expected = 0.01006

        self.assertAlmostEqual(cleaned_rate, expected)

    def persistence_test(self):
        """Assert that all batches and rates were persisted to DB"""
        self.etl.run()

        batches = database.session.query(ForwardRateRunBatch).all()
        self.assertEqual(len(batches), 2)

        rates = database.session.query(ForwardRate).all()
        self.assertEqual(len(rates), 4)
