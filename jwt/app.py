
import argparse
import flask
from flask import (
    Flask, request, url_for, jsonify,
)
import hashlib
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    JWTManager
)

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config["SECRET_KEY"] = "the random string"
app.config["JWT_SECRET_KEY"] = "the random string"
app.config["JWT_TOKEN_LOCATION"] = ["headers","query_string"]

jwt = JWTManager(app)

@app.route("/login", methods=["POST"])
def shitty_login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    m = hashlib.md5()
    m.update(username.encode('utf-8'))
    m.update(password.encode('utf-8'))
    # mock auth to get token
    if m.hexdigest() == "04adb4e2f055c978c9bb101ee1bc5cd4":
        app.logger.error(m.hexdigest())
        access_token = create_access_token(identity=username,expires_delta=False)
        return jsonify(access_token=access_token)
    else:
        app.logger.error(f"{username} {password} {m.hexdigest()}")
        return jsonify({"msg": "Bad username or password"}), 401

@app.route('/blah')
@jwt_required()
def blah():
    param0 = request.args.get('param0')
    return jsonify(param0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-host',type=str,default='0.0.0.0')
    parser.add_argument('-port',type=int,default='5555')
    parser.add_argument('-d','--debug',action='store_true')
    args = parser.parse_args()
    app.run(host=args.host, port=args.port,debug=args.debug)