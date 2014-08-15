import re
from datetime import datetime

from flask import g

from fishhooks.app import github, db, app


PAGER_REGEX = re.compile(r'page=(\d+?)')


def do_get(url, page=None):
    if page is not None:
        url = "%s?page=%d" % (url, page)

    return github.raw_request('GET', url)


def get_list(url, item_parse):
    items = []
    first_page = True
    page = None
    requests = 0

    while first_page or page is not None or requests > app.config['MAX_GITHUB_REQUESTS']:
        response = do_get(url, page=page)
        data = response.json()

        for item in data:
            items.append(item_parse(item))

        first_page = False
        page = has_next(response)
        requests += 1

    return items


def has_next(response):
    if 'link' not in response.headers:
        return None

    link = response.headers['link']
    link_items = link.split(',')
    for link_item in link_items:
        url, rel = link_item.split(';')
        if rel.strip() == 'rel="next"':
            matches = PAGER_REGEX.search(url.strip().lstrip('<').rstrip('>'))
            if not matches:
                return None

            return int(matches.groups()[0])

    return None


def get_user_orgs():
    return get_list('user/orgs', lambda item: {
        'name': item['login']
    })


def get_repo_data(org=None):
    def handle(repo):
        return {
            'name': repo['full_name'],
            'org': org
        }

    return handle


def get_org_repos(org):
    url = 'orgs/%s/repos' % org.org_name
    return get_list(url, get_repo_data(org))


def get_user_repos():
    url = 'user/repos'
    return get_list(url, get_repo_data())


def needs_update(user):
    if user.last_synced_repos is None:
        return True

    expiration = app.config['REPOSITORY_SYNC_EXPIRATION_MINUTES']
    return (datetime.now() - user.last_synced_repos).total_seconds() > expiration * 60


def update_user_repos():
    from fishhooks.models import Repository, Organization

    if g.user is None or not needs_update(g.user):
        return

    repos = []

    Organization.query.filter_by(user=g.user).delete()

    organizations = get_user_orgs()

    for organization in organizations:
        org = Organization(org_name=organization['name'], user=g.user)
        db.session.add(org)
        repos += get_org_repos(org)

    repos += get_user_repos()

    repos = sorted(repos, key=lambda item: item['name'])

    Repository.query.filter_by(user=g.user).delete()

    for repo in repos:
        db.session.add(
            Repository(
                repo_name=repo['name'],
                organization=repo['org'],
                user=g.user
            )
        )

    g.user.last_synced_repos = datetime.now()

    db.session.flush()
    db.session.commit()
