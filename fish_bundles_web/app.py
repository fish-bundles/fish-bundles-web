#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import argparse

from flask import Flask, g, session
from flask.ext.github import GitHub
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__)
github = GitHub()

db = SQLAlchemy()


@app.before_request
def before_request():
    from fish_bundles_web.models import User
    g.user = None
    if 'user' in session:
        g.user = User.query.filter_by(username=session['user']).first()


def parse_arguments(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', type=int, default="5000", help="Port to start the server with.")
    parser.add_argument('--bind', '-b', default="0.0.0.0", help="IP to bind the server to.")
    parser.add_argument('--conf', '-c', default='fish_bundles_web/config/local.conf', help="Path to configuration file.")
    parser.add_argument('--debug', '-d', action='store_true', default=False, help='Indicates whether to run in debug mode.')

    options = parser.parse_args(args)
    return options


def init_app(conf):
    import fish_bundles_web.handlers  # NOQA
    import fish_bundles_web.login  # NOQA
    from fish_bundles_web.bundles import init_bundles  # NOQA
    from fish_bundles_web import config  # NOQA

    config.init_app(app, path=conf)

    github.init_app(app)
    db.init_app(app)

    init_bundles()


def main():
    args = parse_arguments()
    init_app(args.conf)
    app.run(debug=args.debug, host=args.bind, port=args.port)


if __name__ == "__main__":
    main()
