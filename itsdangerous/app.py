import datetime
import os
import traceback
import flask
from flask import Flask, render_template, request, redirect, url_for
from flask_login import (
    login_user, current_user, UserMixin, LoginManager, 
    login_required, logout_user
)
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from itsdangerous.url_safe import URLSafeSerializer


app = Flask(__name__)
app.config['SECRET_KEY']='12345'

class User(UserMixin):
    def __init__(self,user_id):
        self.id = user_id
    def generate_auth_token(self, expiration = 600):
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({ 'id': self.id }).decode('ascii')
    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        return User(data['id'])

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))

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

@app.route('/authenticate')
def authenticate():
    token_dump = request.args.get('token')
    user = User.verify_auth_token(token_dump)
    if user is not None:
        login_user(user)
        return redirect(url_for('home'))
    return unauthorized()

#from flask_httpauth import HTTPBasicAuth
#auth = HTTPBasicAuth()
#@auth.login_required
@app.route('/api/settings')
def settings():
    return "ok"

@app.route('/api/token')
def get_auth_token():
    # TODO: for service accounts, increase expiration.
    user_id = request.args.get('user_id')
    token = User(user_id).generate_auth_token(expiration=600)
    return jsonify({'token': token.decode('ascii')})

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

    if "@ok.com" not in user_id:
        return "ERROR"

    token = User(user_id).generate_auth_token(expiration=600)
    return render_template('submitted.html',status='token generated!',token=token)

@app.route('/home')
@login_required
def home():
    tstamp = datetime.datetime.now()
    return render_template('home.html',tstamp=tstamp)

if __name__ == '__main__':
    ssl_context=('/keystore/cert.pem', '/keystore/key.pem')
    app.run(host="0.0.0.0",port=5000, debug=True,ssl_context=ssl_context)
