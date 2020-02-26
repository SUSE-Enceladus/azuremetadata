#!/usr/bin/env python3

from flask import Flask, request, send_from_directory
from werkzeug.exceptions import NotFound


app = Flask(__name__)


@app.route('/metadata/instance')
def instance():
    api_version = request.args.get("api-version")

    if api_version:
        try:
            return send_from_directory('fixtures', f'metadata-v{api_version}.json')
        except NotFound:
            return f'Unknown API version', 404
    else:
        return f'API version not specified', 400


@app.route('/metadata/attested/document')
def attested_document():
    api_version = request.args.get("api-version")

    if api_version:
        try:
            return send_from_directory('fixtures', f'attested-data-v{api_version}.json')
        except NotFound:
            return f'Unknown API version', 404
    else:
        return f'API version not specified', 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8888')
