import flask

blueprint = flask.Blueprint('dashboard', __name__,
                            template_folder="templates")


@blueprint.route("/")
def home():
    return flask.render_template("dashboard.html")
