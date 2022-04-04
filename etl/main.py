from utils.database import init_db
from etls.pensford_forward_rate_etl import PensfordForwardRateEtl

if __name__ == '__main__':
    init_db()

    etl = PensfordForwardRateEtl()
    etl.run()
