import logging
from gateway_adddon import APIHandler

class KonnectedAPI(APIHandler):
	def __init__(self, manager_proxy, adapter, verbose=False):
		self.adapter = adapter
		APIHandler.__init__(self, 'konnected-adapter', verbose)
		manager_proxy.add_api_handler(self)

	def handle_request(self, request):
		logging.debug(request)
		return super().handle_request(self, request)
