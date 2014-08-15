from flask import request, g, render_template, abort
from ujson import loads, dumps
from sqlalchemy import exists

from fishhooks.app import app, db, github
from fishhooks.decorators import authenticated
from fishhooks.git import update_user_repos


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
    from fishhooks.models import Repository, Organization, Bundle
    update_user_repos()
    orgs = Organization.query.filter_by(user=g.user).order_by(Organization.org_name).all()

    repos = db.session.query(Repository).filter(Repository.user == g.user).filter(
        ~exists().where(Bundle.repo_id == Repository.id)
    ).order_by(Repository.repo_name).all()
    return render_template('create.html', repos=repos, orgs=orgs)


@app.route("/save-bundle", methods=['POST'])
@authenticated
def save_bundle():
    from fishhooks.models import Bundle, BundleFile, Repository

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

    exists = Bundle.query.filter_by(repo=repository).first()
    if exists:
        return dumps({
            'result': 'duplicate_name',
            'slug': None
        })

    repo_readme = github.get("repos/%s/readme" % repository.repo_name)
    contents = repo_readme['content'].decode(repo_readme['encoding'])

    bundle = Bundle(slug=repository.slug, repo=repository, readme=contents, category=category, author=g.user)
    db.session.add(bundle)

    db.session.add(BundleFile(path=repo_readme['name'], file_type='markdown', contents=contents, bundle=bundle))

    db.session.flush()
    db.session.commit()

    return dumps({
        'result': 'ok',
        'slug': bundle.slug
    })
