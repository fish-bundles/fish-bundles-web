import logging
import sys

from cliff.app import App
from cliff.commandmanager import CommandManager
import requests  # NOQA

from fishhooks import __version__
import fishhooks.cli.install  # NOQA


class FishBundlesApp(App):

    log = logging.getLogger('fish-bundles')

    def __init__(self):
        super(FishBundlesApp, self).__init__(
            description='fish-bundles',
            version=__version__,
            command_manager=CommandManager('fb'),
        )


def main(argv=None):
    requests_log = logging.getLogger("requests")
    requests_log.setLevel(logging.WARNING)

    if argv is None:
        argv = sys.argv[1:]
    app = FishBundlesApp()
    return app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
