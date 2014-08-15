from flask import Flask, g, session
from flask.ext.github import GitHub
from flask.ext.sqlalchemy import SQLAlchemy


MARKDOWN = 1
FISH = 2

app = Flask(__name__)
github = GitHub()

db = SQLAlchemy()


@app.before_request
def before_request():
    from fishhooks.models import User
    g.user = None
    if 'user' in session:
        g.user = User.query.filter_by(username=session['user']).first()


def main():
    import fishhooks.handlers  # NOQA
    import fishhooks.login  # NOQA
    from fishhooks.bundles import init_bundles  # NOQA

    app.config['MAX_GITHUB_REQUESTS'] = 15
    app.config['REPOSITORY_SYNC_EXPIRATION_MINUTES'] = 60 * 24 * 7
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/fishhooks'
    app.config['GITHUB_CLIENT_ID'] = '0cd596cdcfb372e75fb0'
    app.config['GITHUB_CLIENT_SECRET'] = '14569ca47300ab7d30ebe784a10efe0f9ce93981'
    app.config['GITHUB_CALLBACK_URL'] = 'http://local.bundles.fish:5000/github-callback'
    app.secret_key = '5CA2086C182A0CFA601896960DF196F09DEA13A14D884F810B52217F6323D8E1'
    github.init_app(app)
    db.init_app(app)

    init_bundles()

    app.run(debug=True)


if __name__ == "__main__":
    main()
