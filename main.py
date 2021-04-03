"""Konnected.io addon for WebThings Gateway."""

from os import path
import functools
import logging
import signal
import sys
import time
import traceback

sys.path.append(path.join(path.dirname(path.abspath(__file__)), 'lib'))

from pkg.konnected_adapter import KonnectedAdapter  # noqa


_DEBUG = False
_ADAPTER = None

print = functools.partial(print, flush=True)


def cleanup(signum, frame):
    """Clean up any resources before exiting."""
    logging.info('CLEANUP exception handler')
    if _ADAPTER is not None:
        _ADAPTER.close_proxy()

    sys.exit(0)


if __name__ == '__main__':
    logging.basicConfig(level=30,
                        format="%(filename)s:%(lineno)s " +
                        "%(levelname)s %(message)s",
                        stream=sys.stdout)
    logging.info('Starting Konnected Addon')

    try:
        signal.signal(signal.SIGINT, cleanup)
        signal.signal(signal.SIGTERM, cleanup)
        _ADAPTER = KonnectedAdapter(verbose=_DEBUG)
        # Wait until proxy stops running. this indicates gateway shut down.
        while _ADAPTER.proxy_running():
            time.sleep(2)
    except Exception as ex:
        print('EXECPTION')
        print(ex)
        print(ex.args)
        print(traceback.format_exception(None,  # <- type(e) by docs but ignore
                                         ex, ex.__traceback__),
              file=sys.stdout)
    logging.info('STOPPED Konnected Addon')
