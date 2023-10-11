from bson.objectid import ObjectId
from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request
from flask.json.provider import JSONProvider
from flask_jwt_extended import *
from flask_jwt_extended.config import config
from jwt.exceptions import ExpiredSignatureError
import json

app = Flask(__name__)
client = MongoClient('mongodb://test:test@13.124.58.16', 27017)
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
# 로그인 페이지


@app.route('/')
def login():
    return render_template('login.html')


'''
* 회원가입
* Author : 김진태
*
'''
# 회원가입 페이지


@app.route('/signup')
def signup():
    return render_template('signup.html')

# ID 중복 체크 확인


@app.route('/checkId')
def check_id():
    id_receive = request.args.get('id_give')
    if id_receive == 'jungle':
        response = {'result': 'failure'}
    else:
        response = {'result': 'success'}

    return jsonify(response)
    '''
    result = db.users.find_one({'id': id_receive})

    if result is not None:
        return 'failure'
    '''


'''
* 메인페이지
* Author : 김병철
*
'''
# 메인 페이지


@app.route('/main')
def main():
    return render_template('main.html', name="정글이", id="jungle02")


if __name__ == '__main__':
    app.run('0.0.0.0', port=8080, debug=True)
