import logging
import sys
from http import HTTPStatus
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import cast, Literal

from indicate_data_exchange_api_client import AggregatedQualityIndicatorResult, AggregationPeriodKind, \
    ProviderResultsPostRequest, DefaultApi, ApiClient, Configuration
from indicate_data_exchange_api_client.rest import ApiException

from indicate_data_exchange_client.config.configuration import load_configuration, DatabaseConfiguration
from indicate_data_exchange_client.db import database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")


def transmit_aggregated_results():
    # Retrieve aggregated quality indicator results for all
    # aggregation periods from the database.
    results = []
    with database.transaction(configuration.database) as session:
        for period_kind in [AggregationPeriodKind.WEEKLY,
                            AggregationPeriodKind.MONTHLY,
                            AggregationPeriodKind.YEARLY]:
            period_name = cast(Literal['weekly', 'monthly', 'yearly'], period_kind.name.lower())
            aggregatedResults = database.read_results(session, period_name)
            count = 0
            for result in aggregatedResults:
                results.append(
                    AggregatedQualityIndicatorResult(
                        indicator_id=result.observation_concept_id,
                        aggregation_period_kind=period_kind,
                        aggregation_period_start=result.period_start,
                        average_value=result.average_value,
                        observation_count=result.observation_count,
                    )
                )
                count += 1
            logger.info("For %7s aggregation, got %6d result(s)", period_name, count)

    # Submit aggregated quality indicator results to the data exchange server.
    logger.info("Submitting aggregated data to %s",
                configuration.data_exchange_endpoint)
    api_configuration = Configuration(host=configuration.data_exchange_endpoint)
    with ApiClient(api_configuration) as api_client:
        # Create an instance of the API class
        api_instance = DefaultApi(api_client)
        payload = ProviderResultsPostRequest(provider_id=configuration.provider_id,
                                             results=results)
        try:
            # Upload quality indicator results for this data provider
            api_instance.provider_results_post(payload)
            logger.info("Submitted aggregated data")
        except ApiException as e:
            logger.error(f"Failed to submit aggregated data: {e}")
            raise e


class TriggerRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/trigger':
            logger.info("Got trigger request")
            try:
                transmit_aggregated_results()
                self.send_response(200)
                self.end_headers()
            except Exception as e:
                message = str(e)
                logger.error(message)
                self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, message)
        else:
            self.send_error(HTTPStatus.NOT_FOUND, '/trigger is the only supported location')
        sys.stdout.flush()


configuration = load_configuration()
logger.info(f"Data provider id is {configuration.provider_id}")
sys.stdout.flush()


endpoint = (configuration.trigger_address, configuration.trigger_port)
logger.info(f"Listening for trigger requests on http://{endpoint[0]}:{endpoint[1]}/trigger")
sys.stdout.flush()
server = HTTPServer(endpoint, TriggerRequestHandler)
server.serve_forever()
