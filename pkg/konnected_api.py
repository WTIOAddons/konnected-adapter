import logging
from gateway_addon import APIHandler

class KonnectedAPI(APIHandler):
	def __init__(self, manager_proxy, adapter, verbose=False):
		logging.debug('konnected-api init')
		self.adapter = adapter
		APIHandler.__init__(self, 'konnected', verbose)
		manager_proxy.add_api_handler(self)

	def handle_request(self, request):
		logging.debug('konnected-api request')
		logging.debug(request)
		return super().handle_request(self, request)
