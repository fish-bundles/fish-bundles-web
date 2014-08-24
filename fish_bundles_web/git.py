import re
from datetime import datetime

from flask import g
from semantic_version import Version
from flask.ext.github import GitHubError

from fish_bundles_web.app import github, db, app


PAGER_REGEX = re.compile(r'page=(\d+?)')


def do_get(url, page=None):
    if page is not None:
        url = "%s?page=%d" % (url, page)

    return github.raw_request('GET', url)


def get_list(url, item_parse, allow_none=False):
    items = []
    first_page = True
    page = None
    requests = 0

    while first_page or page is not None or requests > app.config['MAX_GITHUB_REQUESTS']:
        response = do_get(url, page=page)
        data = response.json()

        for item in data:
            item_data = item_parse(item)
            if item_data is None:
                continue
            items.append(item_data)

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


def __parse_repo_tag(repo):
    def handle(tag_data):
        try:
            Version(tag_data['name'])
        except:
            return None

        return {
            'repo': repo,
            'version': tag_data['name'],
            'commit': tag_data['commit']['sha'],
            'zip': tag_data['zipball_url']
        }
    return handle


def __should_update_tags(repository):
    must_update = False
    if repository.last_updated_tags is None:
        must_update = True
    else:
        expiration = app.config['REPOSITORY_TAGS_EXPIRATION_MINUTES']
        must_update = (datetime.now() - repository.last_updated_tags).total_seconds() > expiration * 60

    return must_update


def get_repo_tags(repo, bundle=None):
    from fish_bundles_web.models import Bundle, Release, Repository, Tag

    repository = Repository.query.filter_by(repo_name=repo).first()
    if repository is None:
        raise RuntimeError("Can't find repository %s. Can't update tags for non-existent repo." % repo)

    if __should_update_tags(repository):
        result = get_list("repos/%s/tags" % repo, __parse_repo_tag(repo))
        Tag.query.filter_by(repository=repository).delete()

        if bundle is None:
            bundle = Bundle.query.filter_by(repo_name=repo).first()

        if bundle is not None:
            Release.query.filter_by(bundle=bundle).delete()

        for tag in result:
            repository.tags.append(Tag(
                tag_name=tag['version'],
                commit_hash=tag['commit'],
                zip_url=tag['zip']
            ))

            if bundle is not None:
                bundle.releases.append(Release(
                    tag_name=tag['version'],
                    commit_hash=tag['commit'],
                    zip_url=tag['zip']
                ))

        repository.last_updated_tags = datetime.now()
        db.session.flush()

    return list(reversed(sorted(repository.taglist, key=lambda item: item['version']['object'])))


def update_config_file(bundle):
    try:
        url = "repos/%s/contents/bundle.yml" % bundle.repo_name
        bundle_config_response = github.get(url)
        bundle_config = bundle_config_response['content'].decode(bundle_config_response['encoding'])
    except GitHubError:
        return None

    bundle.config = bundle_config
    bundle.last_updated_config = datetime.now()

    return bundle_config


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


def update_user_repos(force=False):
    from fish_bundles_web.models import Repository, Organization

    if g.user is None or (not force and not needs_update(g.user)):
        return

    repos = []

    user_repos = dict([(repo.repo_name, repo) for repo in Repository.query.filter_by(user=g.user).all()])
    user_orgs = dict([(org.org_name, org) for org in Organization.query.filter_by(user=g.user).all()])

    organizations = get_user_orgs()

    for organization in organizations:
        org = user_orgs.get(organization['name'], None)
        if org is None:
            org = Organization(org_name=organization['name'], user=g.user)
        db.session.add(org)
        repos += get_org_repos(org)

    repos += get_user_repos()

    repos = sorted(repos, key=lambda item: item['name'])

    for repo in repos:
        if repo['name'] not in user_repos:
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
