from datetime import datetime
from typing import Iterable, List
import requests
from bs4 import BeautifulSoup

from utils.database import insert, attempt_commit
from etls.forward_rate_etl import ForwardRateEtl
from utils.models.forward_rate import ForwardRate
from utils.models.forward_rate_run_batch import ForwardRateRunBatch


class PensfordForwardRateEtl(ForwardRateEtl):
    def __init__(self):
        source = 'Pensford'
        super().__init__(source)

        self.rates_api = 'https://www.pensford.com/resources/forward-curve'

    @staticmethod
    def _fetch_rates_page() -> BeautifulSoup:
        """Fetch rates page from Pensford api"""
        rates_api = 'https://www.pensford.com/resources/forward-curve'
        resp = requests.get(rates_api)

        if not resp.ok:
            raise Exception(f'Failed to fetch rates from {rates_api}')

        return BeautifulSoup(resp.content, 'html.parser')

    @staticmethod
    def _find_rates_tbl(page_soup: BeautifulSoup) -> BeautifulSoup:
        tbl = page_soup.find('table', {'id': 'curve-table'})

        if tbl is None:
            raise Exception('Rate table not found')

        return tbl

    @staticmethod
    def _find_tbl_head_idx(tbl_soup: BeautifulSoup, target_cols: Iterable[str]) -> dict:
        """Find indices of columns by name rather than assuming position in case source site changes slightly"""
        head = tbl_soup.find('thead')

        if head is None:
            raise Exception('Unexpected rate table formatting')

        col_idx_map = {col.lower(): -1 for col in target_cols}

        # traverse available columns in rates table and set the index if it's a target column (case-insensitive)
        for idx, col in enumerate(head.find_all('td')):
            col_txt = col.text.strip().lower()
            if col_idx_map.get(col_txt):
                col_idx_map[col_txt] = idx

        # rename keys to proper case and validate all columns were found
        for col in target_cols:
            val = col_idx_map.pop(col.lower())
            col_idx_map[col] = val

            if val == -1:
                raise Exception(f'Column {col} not found in rate table')

        return col_idx_map

    @staticmethod
    def _yield_rates(tbl_soup: BeautifulSoup) -> List:
        """Generator to yield table rows as list of values in order of column index"""
        body = tbl_soup.find('tbody')

        if body is None:
            raise Exception('No data found in rate table')

        for row in body.find_all('tr'):
            yield [col.text.strip() for col in row.find_all('td')]

    @staticmethod
    def _clean_rate(data_str) -> float:
        """Convert pct string to rate"""
        return float(data_str.split('%')[0]) / 100

    def run(self):
        """Run ETL"""
        # fetch rate table
        rates_page = self._fetch_rates_page()
        tbl = self._find_rates_tbl(rates_page)

        # identify the index of columns we're looking to persist
        target_cols = ('Reset Date', '1-month LIBOR', '1-month Term SOFR')
        cols_idx_map = self._find_tbl_head_idx(tbl, target_cols)

        # create batch rows to record the current run
        # we want separate batches for each rate type because future rate sources may not contain both rates
        libor_batch = ForwardRateRunBatch.create('LIBOR', self.source)
        sofr_batch = ForwardRateRunBatch.create('SOFR', self.source)

        print('Inserting new batch:', libor_batch.to_dict())
        print('Inserting new batch:', sofr_batch.to_dict())

        insert((libor_batch, sofr_batch))

        # yield all table rows
        for rate_row in self._yield_rates(tbl):
            effective_date = datetime.strptime(rate_row[cols_idx_map['Reset Date']], '%m/%d/%Y')
            libor = self._clean_rate(rate_row[cols_idx_map['1-month LIBOR']])
            sofr = self._clean_rate(rate_row[cols_idx_map['1-month Term SOFR']])

            # insert libor and sofr rates to db
            libor_rate = ForwardRate.create(effective_date, libor, libor_batch.batch_id)
            sofr_rate = ForwardRate.create(effective_date, sofr, sofr_batch.batch_id)

            print('Inserting new rate:', libor_rate.to_dict())
            print('Inserting new rate:', sofr_rate.to_dict())

            insert((libor_rate, sofr_rate))

        attempt_commit()
