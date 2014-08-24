from slugify import slugify
import markdown
from sqlalchemy.sql.expression import ClauseElement
from semantic_version import Version

from fish_bundles_web.app import db


def get_or_create(model, defaults=None, **kwargs):
    instance = db.session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        params = dict((k, v) for k, v in kwargs.iteritems() if not isinstance(v, ClauseElement))
        params.update(defaults or {})
        instance = model(**params)
        db.session.add(instance)
        return instance, True


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False, unique=True)
    name = db.Column(db.String(200), unique=True)
    email = db.Column(db.String(255), unique=True)
    location = db.Column(db.String(1200))
    last_synced_repos = db.Column(db.DateTime)


class Bundle(db.Model):
    __tablename__ = "bundles"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(255), nullable=False, unique=True)
    config = db.Column(db.Text, nullable=False)
    readme = db.Column(db.UnicodeText, nullable=False, unique=True)
    category = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime)
    last_updated_at = db.Column(db.DateTime)
    last_updated_config = db.Column(db.DateTime)
    install_count = db.Column(db.Integer, nullable=False, default=0)

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author = db.relationship(User, backref='bundles')

    repo_name = db.Column(db.String(2000), nullable=False, unique=False)
    org_name = db.Column(db.String(2000), nullable=True, unique=False)

    @property
    def readme_html(self):
        return markdown.markdown(self.readme)

    @property
    def all_releases(self):
        return list(reversed(sorted(self.releases, key=lambda item: item.version)))

    @property
    def last_release(self):
        if not self.releases:
            return None

        return self.all_releases[0]


class BundleFile(db.Model):
    __tablename__ = "bundle_files"

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(200), nullable=False)
    file_type = db.Column(db.Integer, nullable=False)
    contents = db.Column(db.LargeBinary, nullable=False)

    bundle_id = db.Column(db.Integer, db.ForeignKey('bundles.id'), nullable=False)
    bundle = db.relationship(Bundle, backref='files')


class Organization(db.Model):
    __tablename__ = "organizations"

    id = db.Column(db.Integer, primary_key=True)
    org_name = db.Column(db.String(255), nullable=False, unique=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship(User)


class Repository(db.Model):
    __tablename__ = "repositories"

    id = db.Column(db.Integer, primary_key=True)
    repo_name = db.Column(db.String(255), nullable=False, unique=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship(User)

    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=True)
    organization = db.relationship(Organization)

    last_updated_tags = db.Column(db.DateTime)

    @property
    def slug(self):
        return slugify(self.repo_name.lower())

    @property
    def username(self):
        return self.repo_name.split('/')[0]

    @property
    def name(self):
        return self.repo_name.split('/')[1]

    @property
    def taglist(self):
        tags = []

        for tag in self.tags:
            tags.append({
                'repo': self.repo_name,
                'version': {
                    'name': tag.tag_name,
                    'object': tag.version,
                },
                'commit': tag.commit_hash,
                'zip': tag.zip_url
            })

        return tags

    @property
    def all_tags(self):
        return list(reversed(sorted(self.tags, key=lambda item: item.version)))

    @property
    def last_tag(self):
        if not self.tags:
            return None

        return self.all_tags[0]


class Release(db.Model):
    __tablename__ = "releases"

    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(255), nullable=False)
    commit_hash = db.Column(db.String(255), nullable=False)
    zip_url = db.Column(db.String(2000), nullable=False)

    bundle_id = db.Column(db.Integer, db.ForeignKey('bundles.id'), nullable=False)
    bundle = db.relationship(Bundle, backref='releases')

    @property
    def version(self):
        return Version(self.tag_name)


class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(255), nullable=False)
    commit_hash = db.Column(db.String(255), nullable=False)
    zip_url = db.Column(db.String(2000), nullable=False)

    repository_id = db.Column(db.Integer, db.ForeignKey('repositories.id'), nullable=False)
    repository = db.relationship(Repository, backref='tags')

    @property
    def version(self):
        return Version(self.tag_name)
