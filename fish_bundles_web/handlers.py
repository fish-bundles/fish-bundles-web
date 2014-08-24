from datetime import datetime
from os.path import abspath, dirname, join

from flask import request, g, render_template, abort, redirect
import markdown
from ujson import loads, dumps
from sqlalchemy import exists

from fish_bundles_web.app import app, db, github
from fish_bundles_web.decorators import authenticated
from fish_bundles_web.git import update_user_repos, get_repo_tags, update_config_file

MARKDOWN = 1
FISH = 2


@app.route("/")
def index():
    from fish_bundles_web.models import Bundle
    bundles = db.session.query(Bundle).order_by(Bundle.install_count.desc())[:50]
    return render_template('index.html', bundles=bundles)


@app.route("/docs")
def docs():
    with open(join(abspath(dirname(__file__)), 'docs.mkd')) as mkd_file:
        mkd = markdown.markdown(mkd_file.read())
    return render_template('docs.html', markdown=mkd)


class BundleResolver(object):
    def __init__(self, bundles):
        self.bundles = bundles
        self.bundle_set = set(self.bundles)

    def resolve(self):
        from fish_bundles_web.models import Bundle

        bundles = []

        db_bundles = db.session.query(Bundle).filter(Bundle.repo_name.in_(self.bundles)).all()
        db_bundle_set = set([db_bundle.repo_name for db_bundle in db_bundles])

        if len(db_bundles) != len(self.bundle_set):
            not_found_bundles = self.bundle_set - db_bundle_set
            return None, list(not_found_bundles)

        for bundle in db_bundles:
            tags = get_repo_tags(bundle.repo_name)
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
            'error':
            (
                "Some bundles could not be found (%s). Maybe there's no bundle "
                "created at bundles.fish for that git repo?" % (
                    ", ".join(error)
                )
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
        ~exists().where(Bundle.repo_name == Repository.repo_name)
    ).order_by(Repository.repo_name).all()
    return render_template('create.html', repos=repos, orgs=orgs)


@app.route("/update-bundles", methods=['GET'])
@authenticated
def update_bundles():
    update_user_repos(force=True)
    return redirect('/create-bundle')


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

    exists = Bundle.query.filter_by(repo_name=repository.repo_name).first()
    if exists:
        return dumps({
            'result': 'duplicate_name',
            'slug': None
        })

    repo_readme = github.get("repos/%s/readme" % repository.repo_name)
    contents = repo_readme['content'].decode(repo_readme['encoding'])
    org_name = repository.organization and repository.organization.org_name or ''

    bundle = Bundle(
        slug=repository.slug, repo_name=repository.repo_name, org_name=org_name, readme=contents, category=category,
        author=g.user, created_at=datetime.now(), last_updated_at=datetime.now()
    )

    config_file = update_config_file(bundle)
    if config_file is None:
        return dumps({
            'result': 'no_config',
            'slug': None
        })

    db.session.add(bundle)

    # just pre-loading tags
    get_repo_tags(repository.repo_name, bundle)

    db.session.add(BundleFile(path=repo_readme['name'], file_type=MARKDOWN, contents=contents, bundle=bundle))

    db.session.flush()
    db.session.commit()

    return dumps({
        'result': 'ok',
        'slug': bundle.slug
    })
