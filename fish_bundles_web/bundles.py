from flask.ext.assets import Environment, Bundle

from fish_bundles_web.app import app

assets = Environment(app)


def init_bundles():
    base_libs = [
        'vendor/jquery/dist/jquery.js',
        'vendor/datatables/media/js/jquery.dataTables.js',
        'scripts/dataTables.bootstrap.js',
        # 'vendor/bootstrap-sass-official/assets/javascripts/bootstrap.js',
    ]
    js = Bundle(*base_libs, filters=['jsmin'], output='scripts/fish-bundles.base.min.js')
    assets.register('js_base', js)

    app_files = [
        'scripts/main.coffee',
        'scripts/create.coffee',
        'scripts/header.coffee',
    ]
    js = Bundle(*app_files, filters=['coffeescript', 'jsmin'], output='scripts/fish-bundles.app.min.js')
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
        'vendor/datatables/media/css/jquery.dataTables.css',
        'stylesheets/dataTables.bootstrap.css',
    ]

    css = Bundle(*css_files, filters=['cssmin'], output='stylesheets/fish-bundles.base.min.css')
    assets.register('css_base', css)

    css_files = [
        'sass/main.scss'
    ]

    css = Bundle(*css_files, depends=["**/*.scss"], filters=['compass', 'cssmin'], output='stylesheets/fish-bundles.min.css')
    assets.register('css_app', css)

    if app.debug:
        assets.auto_build = True
        assets.debug = True
        assets.manifest = "file"
        assets.cache = False
