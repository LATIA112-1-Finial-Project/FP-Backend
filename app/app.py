
from flask import Flask
from api import *
from model import *

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.url_map.strict_slashes = False
api2prefix = [
    (user_api, '/api/v1/user'),
]
for api, prefix in api2prefix:
    app.register_blueprint(api, url_prefix=prefix)

if __name__ == "__main__":
    app.run(debug=True, port=8080)
