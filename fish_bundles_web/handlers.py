from datetime import datetime

from flask import request, g, render_template, abort
from ujson import loads, dumps
from sqlalchemy import exists

from fish_bundles_web.app import app, db, github
from fish_bundles_web.decorators import authenticated
from fish_bundles_web.git import update_user_repos, get_repo_tags

MARKDOWN = 1
FISH = 2


@app.route("/")
def index():
    from fish_bundles_web.models import Bundle
    bundles = db.session.query(Bundle)[:50]
    return render_template('index.html', bundles=bundles)


class BundleResolver(object):
    def __init__(self, bundles):
        self.bundles = bundles
        self.bundle_set = set(self.bundles)

    def resolve(self):
        from fish_bundles_web.models import Bundle, Repository

        bundles = []

        db_bundles = db.session.query(Bundle).filter(Repository.repo_name.in_(self.bundles)).all()
        db_bundle_set = set([db_bundle.repo.repo_name for db_bundle in db_bundles])

        if len(db_bundles) != len(self.bundle_set):
            not_found_bundles = self.bundle_set - db_bundle_set
            return None, list(not_found_bundles)

        for bundle in db_bundles:
            tags = get_repo_tags(bundle.repo.repo_name)
            last_tag = tags[0]
            bundles.append({
                'repo': last_tag['repo'],
                'version': last_tag['version']['name'],
                'commit': last_tag['commit'],
                'zip': last_tag['zip']
            })
            bundle.install_count += 1

        db.session.flush()
        return bundles, None


@app.route("/my-bundles")
def my_bundles():
    bundles = loads(str(request.args.get('bundles', '')))
    resolver = BundleResolver(bundles)

    resolved, error = resolver.resolve()

    if error is not None:
        db.session.rollback()
        return dumps({
            'result': 'bundles-not-found',
            'bundles': None,
            'error': "Some bundles could not be found (%s). Maybe there's no bundle created at bundles.fish for that git repo?" % (
                ", ".join(error)
            )
        })

    db.session.commit()

    return dumps({
        'result': 'bundles-found',
        'bundles': resolved
    })


@app.route("/bundles/<bundle_slug>")
def show_bundle(bundle_slug):
    from fish_bundles_web.models import Bundle

    bundle = Bundle.query.filter_by(slug=bundle_slug).first()
    if not bundle:
        abort(404)

    return render_template('show_bundle.html', bundle=bundle)


@app.route("/create-bundle", methods=['GET'])
@authenticated
def create_bundle():
    from fish_bundles_web.models import Repository, Organization, Bundle
    update_user_repos()
    orgs = Organization.query.filter_by(user=g.user).order_by(Organization.org_name).all()

    repos = db.session.query(Repository).filter(Repository.user == g.user).filter(
        ~exists().where(Bundle.repo_id == Repository.id)
    ).order_by(Repository.repo_name).all()
    return render_template('create.html', repos=repos, orgs=orgs)


@app.route("/save-bundle", methods=['POST'])
@authenticated
def save_bundle():
    from fish_bundles_web.models import Bundle, BundleFile, Repository

    bundle_data = loads(request.form['obj'])
    try:
        category = int(bundle_data['category'])
    except ValueError:
        category = 4

    repository = Repository.query.filter_by(repo_name=bundle_data['repository'], user=g.user).first()

    if repository is None:
        return dumps({
            'result': 'repository_not_found',
            'slug': None
        })

    # just pre-loading tags
    get_repo_tags(repository.repo_name)

    exists = Bundle.query.filter_by(repo=repository).first()
    if exists:
        return dumps({
            'result': 'duplicate_name',
            'slug': None
        })

    repo_readme = github.get("repos/%s/readme" % repository.repo_name)
    contents = repo_readme['content'].decode(repo_readme['encoding'])

    bundle = Bundle(slug=repository.slug, repo=repository, readme=contents, category=category, author=g.user, last_updated_at=datetime.now())
    db.session.add(bundle)

    db.session.add(BundleFile(path=repo_readme['name'], file_type=MARKDOWN, contents=contents, bundle=bundle))

    db.session.flush()
    db.session.commit()

    return dumps({
        'result': 'ok',
        'slug': bundle.slug
    })
