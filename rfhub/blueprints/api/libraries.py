"""
This provides the view functions for the /api/libraries endpoints
"""

import flask

from rfhub import app


class ApiEndpoint(object):
    def __init__(self, blueprint):
        blueprint.add_url_rule("/libraries/", view_func=self.get_libraries)
        blueprint.add_url_rule("/libraries/<collection_id>", view_func=self.get_library)

    @staticmethod
    def get_libraries():
        kwdb = app.hub.kwdb

        query_pattern = flask.request.args.get('pattern', "*").strip().lower()
        libraries = kwdb.get_collections(query_pattern)

        return flask.jsonify(libraries=libraries)

    @staticmethod
    def get_library(collection_id):
        # if collection_id is a library _name_, redirect
        print("get_library: collection_id=", collection_id)
        kwdb = app.hub.kwdb
        collection = kwdb.get_collection(collection_id)
        return flask.jsonify(collection=collection)
