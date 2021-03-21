import os
import sys
import traceback
import datetime

from flask import (
    Flask, render_template, request, redirect, url_for,
    jsonify, 
)
from flask_login import (
    login_user, current_user, UserMixin, LoginManager, 
    login_required, logout_user,
)
from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer, 
    BadSignature, SignatureExpired,
)

from itsdangerous.url_safe import (
    URLSafeSerializer, URLSafeTimedSerializer,
)
from flask_httpauth import HTTPBasicAuth


app = Flask(__name__)
app.config['SECRET_KEY']=os.environ['SECRET_KEY']
SK = app.config['SECRET_KEY']
EXPIRATION_SECONDS = 10

login_manager = LoginManager()
login_manager.init_app(app)
auth = HTTPBasicAuth() # for rest api

class User(UserMixin):
    def __init__(self,user_id):
        self.id = user_id

    def generate_auth_token(self):
        s = URLSafeTimedSerializer(SK).signer(SK)
        token = s.sign(self.id)
        token = token.decode('utf-8')
        return token

    @staticmethod
    def verify_auth_token(token,max_age=EXPIRATION_SECONDS):
        s = URLSafeTimedSerializer(SK).signer(SK)
        try:
            token = token.encode('utf-8')
            user_id = s.unsign(token,max_age=max_age)
            user_id = user_id.decode('utf-8')
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        return User(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    response = jsonify({"error":"unauthorized request."})
    return response, 401

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
    
@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/ping')
def ping():
    return jsonify({"status":"pong"})

@app.route('/authenticate')
def authenticate():
    token = request.args.get('token')
    user = User.verify_auth_token(token)
    if user is not None:
        login_user(user)
        return redirect(url_for('home'))
    return unauthorized()

@auth.verify_password
def verify_password(username_or_token, password):
    user = User.verify_auth_token(username_or_token,max_age=None)
    if not user:
        return False
    return True

@app.route('/api/resource')
@auth.login_required
def settings():
    return jsonify({'data':'blah'})

# not a rest call! for dev to pass to devs.
def get_auth_token(user_id):
    token = User(user_id).generate_auth_token()
    return { 'token': token }

@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if request.method == 'GET':
        return '''
               <form action='login' method='POST'>
                <input type='text' name='email' id='email' placeholder='email'/>
                <input type='submit' name='submit'/>
               </form>
               '''

    user_id = request.form['email']

    if "@" not in user_id:
        return jsonify({"error":"invalid email."})

    token = User(user_id).generate_auth_token()
    return render_template('submitted.html',status='token generated!',token=token,expiration_sec=EXPIRATION_SECONDS)

@app.route('/home')
@login_required
def home():
    tstamp = datetime.datetime.now()
    return render_template('home.html',tstamp=tstamp)

if __name__ == '__main__':
    ssl_context=('/keystore/cert.pem', '/keystore/key.pem')
    for key in ssl_context:
        if not os.path.exists(key):
            raise ValueError('pem file not found')
    print(get_auth_token('itsarobot'))
    app.run(host="0.0.0.0",port=5000, debug=True,ssl_context=ssl_context)
