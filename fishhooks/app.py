from flask import Flask, request, url_for, flash, redirect
from flask.ext.github import GitHub

app = Flask(__name__)
github = GitHub()


@app.route("/")
def index():
    return '<a href="%s">login!</a>' % url_for('login')


@app.route('/login')
def login():
    return github.authorize()


@app.route('/github-callback')
@github.authorized_handler
def authorized(oauth_token):
    next_url = request.args.get('next') or url_for('index')
    if oauth_token is None:
        flash("Authorization failed.")
        return redirect(next_url)

    save_user(oauth_token)
    return redirect(next_url)


def save_user(oauth_token):
    print "saving user %s" % oauth_token


def main():
    app.config['GITHUB_CLIENT_ID'] = '0cd596cdcfb372e75fb0'
    app.config['GITHUB_CLIENT_SECRET'] = '14569ca47300ab7d30ebe784a10efe0f9ce93981'
    app.config['GITHUB_CALLBACK_URL'] = 'http://local.fish-hooks.com:5000/github-callback'
    github.init_app(app)

    app.run(debug=True)


if __name__ == "__main__":
    main()
