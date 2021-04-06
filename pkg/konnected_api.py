import logging
from gateway_addon import APIHandler

class KonnectedAPI(APIHandler):
	def __init__(self, adapter, verbose=False):
		logging.debug('konnected-api init')
		self.adapter = adapter
		APIHandler.__init__(self, 'konnected-api', verbose)
		logging.debug('konnected-api finished')

	def handle_request(self, request):
		logging.debug('konnected-api request')
		logging.debug(request)
		return super().handle_request(self, request)
