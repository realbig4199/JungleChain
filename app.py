from bson.objectid import ObjectId
from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request
from flask.json.provider import JSONProvider
from flask_jwt_extended import *
from flask_jwt_extended.config import config
from jwt.exceptions import ExpiredSignatureError
from datetime import datetime,timedelta
import json
import time # https://kimxavi.tistory.com/entry/python-JWT-example
import jwt
secret_key = 'junglechain'

app = Flask(__name__)
client = MongoClient('mongodb://test:test@13.124.58.16',27017)
db = client.dbjungle

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

class CustomJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return json.dumps(obj, **kwargs, cls=CustomJSONEncoder)

    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)
    
app.json = CustomJSONProvider(app)


# URL 별로 함수명이 같거나,
# route('/') 등의 주소가 같으면 안됩니다.
'''
* 로그인
* Author : 홍선우
* 
'''
# 초기 페이지
@app.route('/')
def home():
    return render_template('login.html')

# 로그인
@app.route('/login', methods=['POST'])
def user_login() :
    # 로그인 정보 유효성 확인 코드
    id_recieve = request.form['id_give']
    pw_recieve = request.form['pw_give']
     
    result = db.users.find_one({'id': id_recieve, 'pw': pw_recieve}) # id, 암호화된pw을 가지고 해당 유저를 찾습니다.

    # 로그인 정보 유효할 시 token 생성 후 client로 전달
    if result is not None:
         # JWT 토큰 생성
        payload = {
            'id': id_recieve,
            'exp': datetime.utcnow() + timedelta(hours=60) # 24시간 로그인 유지
        }
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디 또는 비밀번호가 틀렸습니다.'})

# 메인 페이지
app.route('/find')
def find():
    token_receive = request.cookies.get('mytoken')

    try:
        payload = jwt.decode(token_receive, secret_key, algorithms=['HS256']) # token디코딩합니다.
        userinfo = db.users.find_one({'id': payload['id']}, {'_id': 0})
        return render_template("Main.html", user_info=userinfo)
    
    except jwt.ExpiredSignatureError:
        return redirect(url_for("/", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("/", msg="로그인 정보가 존재하지 않습니다."))
'''
* 회원가입
* Author : 김진태
*
'''
#회원가입 페이지
@app.route('/signup')
def signup():
    return render_template('signup.html')

'''
* 메인페이지
* Author : 김병철
*
'''
#메인 페이지
@app.route('/main')
def main():
    return render_template('main.html', name="정글이", id="jungle02")


if __name__ == '__main__':
    app.run('0.0.0.0', port=8080, debug=True)