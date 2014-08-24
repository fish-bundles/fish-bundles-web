#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file is part of tornado_angular.
# https://github.com/heynemann/tornado-angular

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2014 Bernardo Heynemann heynemann@gmail.com

from derpconf.config import Config, generate_config

MINUTE = 60
HOUR = 60 * MINUTE
DAY = 24 * HOUR

Config.define('APP_SECRET_KEY', None, 'SECRET KEY TO CONFIGURE BZZ', 'Authentication')

Config.define('MAX_GITHUB_REQUESTS', 15, 'Max number of github requests to do sequentially', 'GitHub')
Config.define('REPOSITORY_SYNC_EXPIRATION_MINUTES', 7 * DAY / MINUTE, 'Repository sync expiration', 'GitHub')
Config.define('REPOSITORY_TAGS_EXPIRATION_MINUTES', 3, 'Repository sync expiration', 'GitHub')

Config.define('SQLALCHEMY_DATABASE_URI', 'mysql://root@localhost/fish_bundles_web', 'MySQL connection string', 'DB')

Config.define('GITHUB_CLIENT_ID', '0cd596cdcfb372e75fb0', 'Github Client Id', 'GitHub')
Config.define('GITHUB_CLIENT_SECRET', '14569ca47300ab7d30ebe784a10efe0f9ce93981', 'Github Client Secret', 'GitHub')
Config.define('GITHUB_CALLBACK_URL', 'http://local.bundles.fish:5000/github-callback', 'Github Callback URL', 'GitHub')


def init_app(app, path=None):
    conf = Config.load(path)
    for conf_option, _ in conf.items.items():
        app.config[conf_option] = conf[conf_option]

    app.secret_key = app.config['APP_SECRET_KEY']

if __name__ == '__main__':
    generate_config()
