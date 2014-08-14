from fishhooks.app import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False, unique=True)
    name = db.Column(db.String(200), unique=True)
    email = db.Column(db.String(255), unique=True)
    location = db.Column(db.String(1200))


class Bundle(db.Model):
    __tablename__ = "bundles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    slug = db.Column(db.String(50), nullable=False)
    category = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime())

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author = db.relationship(User, backref='bundles')


class BundleFile(db.Model):
    __tablename__ = "bundle_files"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    file_type = db.Column(db.Integer, nullable=False)
    contents = db.Column(db.LargeBinary, nullable=False)

    bundle_id = db.Column(db.Integer, db.ForeignKey('bundles.id'), nullable=False)
    bundle = db.relationship(Bundle, backref='files')
