import sys
from contextlib import contextmanager
from typing import List, Literal

import logging
import sqlalchemy
from sqlalchemy import select
from sqlalchemy.orm import Session

from indicate_data_exchange_client.config.configuration import DatabaseConfiguration
from indicate_data_exchange_client.db.model import WeeklyQualityIndicatorResults, AggregatedQualityIndicatorResults, \
    MonthlyQualityIndicatorResults, YearlyQualityIndicatorResults


logger = logging.getLogger("main")


@contextmanager
def transaction(configuration: DatabaseConfiguration):
    def construct_database_url(host=configuration.host,
                               port=configuration.port,
                               database=configuration.database,
                               user=configuration.user,
                               password=configuration.password):
        return f"postgresql://{user}:{password}@{host}:{str(port)}/{database}"
    database_url = construct_database_url()
    logger.info(f"Connecting to database at {construct_database_url(password='*'*len(configuration.password))}")
    sys.stdout.flush()
    engine = sqlalchemy.create_engine(database_url)
    with Session(engine) as session:
        yield session
        session.commit()


def read_results(session, aggregation_period: Literal['weekly', 'monthly', 'yearly']) -> List[AggregatedQualityIndicatorResults]:
    if aggregation_period == 'weekly':
        table = WeeklyQualityIndicatorResults
    elif aggregation_period == 'monthly':
        table = MonthlyQualityIndicatorResults
    else:
        assert(aggregation_period == 'yearly')
        table = YearlyQualityIndicatorResults
    return session.scalars(select(table))
