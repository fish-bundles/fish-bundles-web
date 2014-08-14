from functools import wraps

from flask import Flask, request, url_for, flash, redirect, g, session, render_template, abort
from flask.ext.github import GitHub
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment, Bundle
from ujson import loads, dumps
from slugify import slugify

MARKDOWN = 1
FISH = 2

app = Flask(__name__)
github = GitHub()
assets = Environment(app)

db = SQLAlchemy()


@app.before_request
def before_request():
    from fishhooks.models import User
    g.user = None
    if 'user' in session:
        g.user = User.query.filter_by(username=session['user']).first()


def authenticated(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = g.user
        if not user:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/bundles/<bundle_slug>")
def show_bundle(bundle_slug):
    from fishhooks.models import Bundle

    bundle = Bundle.query.filter_by(slug=bundle_slug).first()
    if not bundle:
        abort(404)

    return render_template('show_bundle.html', bundle=bundle)


@app.route("/create-bundle", methods=['GET'])
@authenticated
def create_bundle():
    return render_template('create.html')


@app.route("/save-bundle", methods=['POST'])
@authenticated
def save_bundle():
    from fishhooks.models import Bundle, BundleFile

    bundle_data = loads(request.form['obj'])
    try:
        category = int(bundle_data['category'])
    except ValueError:
        category = 4

    exists = Bundle.query.filter_by(name=bundle_data['name']).first()
    if exists:
        return dumps({
            'result': 'duplicate_name',
            'slug': None
        })

    bundle = Bundle(name=bundle_data['name'], slug=slugify(bundle_data['name'].lower()), category=category, author=g.user)
    db.session.add(bundle)

    db.session.add(BundleFile(name='readme.md', file_type=MARKDOWN, contents=bundle_data['readme'], bundle=bundle))
    db.session.add(BundleFile(name='%s.fish' % bundle.slug, file_type=FISH, contents=bundle_data['main'], bundle=bundle))

    db.session.flush()
    db.session.commit()

    return dumps({
        'result': 'ok',
        'slug': bundle.slug
    })


@app.route('/authenticate')
def authenticate():
    return github.authorize()


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/github-callback')
@github.authorized_handler
def authorized(oauth_token):
    next_url = request.args.get('next') or url_for('index')
    if oauth_token is None:
        flash("Authorization failed.")
        return redirect(next_url)

    save_user_token(oauth_token)
    user_data = get_user_data()
    user = get_user_from_db(user_data)
    session['user'] = user.username

    return redirect(next_url)


def get_user_from_db(user_data):
    from fishhooks.models import User
    user = User.query.filter_by(username=user_data['login']).first()
    if user is not None:
        return user

    login = user_data['login']
    user = User(
        username=login,
        name=user_data.get('name', login),
        email=user_data.get('email', None),
        location=user_data.get('location', None)
    )
    db.session.add(user)
    db.session.commit()

    return user


def get_user_data():
    return github.get('user')
    # {u'avatar_url': u'https://avatars.githubusercontent.com/u/60965?v=2',
    # u'bio': None,
    # u'blog': u'http://www.heynemann.com.br',
    # u'company': u'Globo.com',
    # u'created_at': u'2009-03-07T01:46:32Z',
    # u'email': u'heynemann@gmail.com',
    # u'events_url': u'https://api.github.com/users/heynemann/events{/privacy}',
    # u'followers': 346,
    # u'followers_url': u'https://api.github.com/users/heynemann/followers',
    # u'following': 174,
    # u'following_url': u'https://api.github.com/users/heynemann/following{/other_user}',
    # u'gists_url': u'https://api.github.com/users/heynemann/gists{/gist_id}',
    # u'gravatar_id': u'eca21e5e47811c60e03087fc311e1d29',
    # u'hireable': False,
    # u'html_url': u'https://github.com/heynemann',
    # u'id': 60965,
    # u'location': u'Rio de Janeiro, RJ, Brazil',
    # u'login': u'heynemann',
    # u'name': u'Bernardo Heynemann',
    # u'organizations_url': u'https://api.github.com/users/heynemann/orgs',
    # u'public_gists': 47,
    # u'public_repos': 136,
    # u'received_events_url': u'https://api.github.com/users/heynemann/received_events',
    # u'repos_url': u'https://api.github.com/users/heynemann/repos',
    # u'site_admin': False,
    # u'starred_url': u'https://api.github.com/users/heynemann/starred{/owner}{/repo}',
    # u'subscriptions_url': u'https://api.github.com/users/heynemann/subscriptions',
    # u'type': u'User',
    # u'updated_at': u'2014-08-10T20:14:46Z',
    # u'url': u'https://api.github.com/users/heynemann'}


def save_user_token(oauth_token):
    g.user = {
        'token': oauth_token
    }
    print "saving user %s" % oauth_token


@github.access_token_getter
def token_getter():
    user = g.user
    if user is not None:
        return user['token']


def main():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/fishhooks'
    app.config['GITHUB_CLIENT_ID'] = '0cd596cdcfb372e75fb0'
    app.config['GITHUB_CLIENT_SECRET'] = '14569ca47300ab7d30ebe784a10efe0f9ce93981'
    app.config['GITHUB_CALLBACK_URL'] = 'http://local.bundles.fish:5000/github-callback'
    app.secret_key = '5CA2086C182A0CFA601896960DF196F09DEA13A14D884F810B52217F6323D8E1'
    github.init_app(app)
    db.init_app(app)

    init_bundles()

    app.run(debug=True)


def init_bundles():
    base_libs = [
        'vendor/jquery/dist/jquery.js',
        'vendor/bootstrap-sass-official/assets/javascripts/bootstrap.js',
        'vendor/codemirror/lib/codemirror.js',
        'vendor/codemirror/addon/display/fullscreen.js',
        'scripts/markdown.js',
        'scripts/shell.js',
    ]
    js = Bundle(*base_libs, filters=['jsmin'], output='fish-bundles.base.min.js')
    assets.register('js_base', js)

    app_files = [
        'scripts/main.coffee',
        'scripts/create.coffee',
    ]
    js = Bundle(*app_files, filters=['coffeescript', 'jsmin'], output='fish-bundles.app.min.js')
    assets.register('js_app', js)

    app.config['COMPASS_PLUGINS'] = ['bootstrap-sass']
    app.config['COMPASS_CONFIG'] = dict(
        css_dir="stylesheets",
        sass_dir="sass",
        images_dir="images",
        javascripts_dir="scripts",
        relative_assets=True,
    )

    css_files = [
        'vendor/codemirror/lib/codemirror.css',
        'vendor/codemirror/addon/display/fullscreen.css',
        'vendor/codemirror/theme/monokai.css',
    ]

    css = Bundle(*css_files, filters=['cssmin'], output='fish-bundles.base.min.css')
    assets.register('css_base', css)

    css_files = [
        'sass/main.scss'
    ]

    css = Bundle(*css_files, depends=["**/*.scss"], filters=['compass', 'cssmin'], output='fish-bundles.min.css')
    assets.register('css_app', css)

    assets.auto_build = True
    assets.debug = True
    assets.manifest = "file"
    assets.cache = False


if __name__ == "__main__":
    main()
