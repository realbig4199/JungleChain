from bson.objectid import ObjectId
from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request
from flask.json.provider import JSONProvider
from flask_jwt_extended import *
from flask_jwt_extended.config import config
from jwt.exceptions import ExpiredSignatureError
import json

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
#로그인 페이지
@app.route('/')
def login():
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
            'exp': datetime.utcnow() + timedelta(hours=2)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디 또는 비밀번호가 틀렸습니다.'})

'''
* 회원가입
* Author : 김진태
*
'''
#회원가입 페이지
@app.route('/signup')
def signup():
    return render_template('signup.html')

# 회원가입
@app.route("/signup", methods=["POST"])
def join():
   # 사용자 정보 받아오기
   id_recieve = request.form["id_give"]
   pw_recieve = request.form["pw_give"]
   name_recieve = request.form["name_give"]

   mbti_recieve = request.form["mbti_give"]
   region_recieve = request.form["region_give"]
   smoking_recieve = request.form["smoking_give"]
   gender_recieve = request.form["gender_give"]
   university_recieve = request.form["university_give"]
   major_recieve = request.form["major_give"]

   result = db.users.find_one({'id': id_recieve})
   
   if result is not None:
        return jsonify({'result': 'fail', 'msg': 'ID 중복확인을 해주세요'})
   else:
        db.users.insert_one({'id': id_recieve, 'pw': pw_recieve, 'name_give': name_recieve, "mbti":mbti_recieve, 
           "region":region_recieve, "smoking":smoking_recieve, "gender":gender_recieve, 
           "university":university_recieve, "major":major_recieve, "canuse":'O'})
        return jsonify({'result': 'success'})

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
    app.run('0.0.0.0', port=5000, debug=True)
