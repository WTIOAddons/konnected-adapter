"""API for Konnected adapter for WebThings Gateway."""

import logging
from gateway_addon import APIHandler


class KonnectedAPI(APIHandler):
    def __init__(self, adapter, verbose=False):
        self.adapter = adapter
        APIHandler.__init__(self, 'konnected-api', verbose)

    def handle_request(self, request):
        logging.debug("handle request")
        return super().handle_request(self, request)
