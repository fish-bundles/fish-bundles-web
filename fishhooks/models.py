from slugify import slugify
import markdown
from sqlalchemy.sql.expression import ClauseElement

from fishhooks.app import db


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
    readme = db.Column(db.UnicodeText, nullable=False, unique=True)
    category = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime)
    last_updated_at = db.Column(db.DateTime)

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author = db.relationship(User, backref='bundles')

    repo_id = db.Column(db.Integer, db.ForeignKey('repositories.id'), nullable=False)
    repo = db.relationship('Repository')

    @property
    def readme_html(self):
        return markdown.markdown(self.readme)


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

    @property
    def slug(self):
        return slugify(self.repo_name.lower())

    @property
    def username(self):
        return self.repo_name.split('/')[0]

    @property
    def name(self):
        return self.repo_name.split('/')[1]
