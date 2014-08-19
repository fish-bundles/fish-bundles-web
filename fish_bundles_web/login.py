from flask import request, url_for, flash, redirect, session, render_template

from fish_bundles_web.app import app, db, github


@app.route('/authenticate')
def authenticate():
    return github.authorize(scope='user:email,read:org')


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
    from fish_bundles_web.models import User
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
    session['oauth_token'] = oauth_token


@github.access_token_getter
def token_getter():
    oauth_token = session.get('oauth_token')
    if oauth_token is not None:
        return oauth_token
