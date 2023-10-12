from bson.objectid import ObjectId
from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request
from flask.json.provider import JSONProvider
from flask_jwt_extended import *
from flask_jwt_extended.config import config
from jwt.exceptions import ExpiredSignatureError
from datetime import datetime, timedelta
import json
import time  # https://kimxavi.tistory.com/entry/python-JWT-example
import jwt
secret_key = 'junglechain'

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
# 초기 페이지


@app.route('/')
def home():
    return render_template('login.html')

# 로그인


@app.route('/login', methods=['POST'])
def user_login():
    # 로그인 정보 유효성 확인 코드
    id_recieve = request.form['id_give']
    pw_recieve = request.form['pw_give']

    # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
    result = db.users.find_one({'id': id_recieve, 'pw': pw_recieve})

    # 로그인 정보 유효할 시 token 생성 후 client로 전달
    if result is not None:
        # JWT 토큰 생성
        payload = {
            'id': id_recieve,
            'exp': datetime.utcnow() + timedelta(hours=60)  # 24시간 로그인 유지
        }
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디 또는 비밀번호가 틀렸습니다.'})

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
    img_recieve = request.form["img_give"]

    result = db.users.find_one({'id': id_recieve})

    if result is not None:
        return jsonify({'result': 'fail', 'msg': 'ID 중복확인을 해주세요'})
    else:
        db.users.insert_one({
            'user_id': id_recieve,
            'user_pw': pw_recieve,
            'user_name': name_recieve,
            "mbti": mbti_recieve,
            "region": region_recieve,
            "smoking": smoking_recieve,
            "gender": gender_recieve,
            "univ": university_recieve,
            "major": major_recieve,
            "img": img_recieve
        })
        return jsonify({'result': 'success'})


# 메인 페이지
app.route('/find')


def find():
    token_receive = request.cookies.get('mytoken')

    try:
        # token디코딩합니다.
        payload = jwt.decode(token_receive, secret_key, algorithms=['HS256'])
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
# 회원가입 페이지


@app.route('/signup')
def signup():
    return render_template('signup.html')


'''
* 메인페이지
* Author : 김병철
*
'''
# 메인 페이지
@app.route('/main')
def main():

    #[FIXME] JWT 인증 기능 구현 필요

    return render_template('main.html', name="정글이", id="jungle")


@app.route('/main/search', methods=['POST'])
def getNetworkGraph():
    jsonData = json.loads(request.data)

    my_data = db.user.find_one({'user_id' : 'jungle'})
    
    mbti_flag = jsonData.get('mbtiBtn')
    region_flag = jsonData.get('locBtn')
    univ_flag = jsonData.get('schoolBtn')
    major_flag = jsonData.get('majBtn')
    gender_flag = jsonData.get('genBtn')
    smoking_flag = jsonData.get('smkBtn')

    result_data = {}
    friend_data = {}

    queryString = {
        'user_id' : { '$ne' : 'jungle' }
    }
    if mbti_flag:
        queryString['mbti'] = my_data["mbti"]
        mbti_data = list(db.user.find(queryString))

        for data_set in mbti_data:
            user_id = data_set["user_id"]
            if "img" in data_set:
                img_id = data_set["img"]
            else :
                img_id = "https://cdn4.iconfinder.com/data/icons/seo-and-data/500/pencil-gear-128.png"
            if user_id not in result_data:
                result_data[user_id] = 1
                friend_data[user_id] = img_id
            else :
                result_data[user_id] += 1
        del queryString['mbti']

    if region_flag:
        queryString['region'] = my_data["region"]
        region_data = list(db.user.find(queryString))

        for data_set in region_data:
            user_id = data_set["user_id"]
            if "img" in data_set:
                img_id = data_set["img"]
            else :
                img_id = "https://cdn4.iconfinder.com/data/icons/seo-and-data/500/pencil-gear-128.png"
            if user_id not in result_data:
                result_data[user_id] = 1
                friend_data[user_id] = img_id
            else :
                result_data[user_id] += 1

        del queryString['region']
    if smoking_flag:
        queryString['smoking'] = my_data['smoking']
        smoking_data = list(db.user.find(queryString))

        for data_set in smoking_data:
            user_id = data_set["user_id"]
            if "img" in data_set:
                img_id = data_set["img"]
            else :
                img_id = "https://cdn4.iconfinder.com/data/icons/seo-and-data/500/pencil-gear-128.png"
            if user_id not in result_data:
                result_data[user_id] = 1
                friend_data[user_id] = img_id
            else :
                result_data[user_id] += 1

        del queryString['smoking']

    if univ_flag:
        queryString['univ'] = my_data['univ']
        univ_data = list(db.user.find(queryString))
        
        for data_set in univ_data:
            user_id = data_set["user_id"]
            if "img" in data_set:
                img_id = data_set["img"]
            else :
                img_id = "https://cdn4.iconfinder.com/data/icons/seo-and-data/500/pencil-gear-128.png"
            if user_id not in result_data:
                result_data[user_id] = 1
                friend_data[user_id] = img_id
            else :
                result_data[user_id] += 1

        del queryString['univ']

    if major_flag:
        queryString['major'] = my_data['major']
        major_data = list(db.user.find(queryString))
        
        for data_set in major_data:
            user_id = data_set["user_id"]

            if "img" in data_set:
                img_id = data_set["img"]
            else :
                img_id = "https://cdn4.iconfinder.com/data/icons/seo-and-data/500/pencil-gear-128.png"

            if user_id not in result_data:
                result_data[user_id] = 1
                friend_data[user_id] = img_id
            else :
                result_data[user_id] += 1

        del queryString['major']

    if gender_flag:
        queryString['gender'] = my_data['gender']
        gender_data = list(db.user.find(queryString))
        
        for data_set in gender_data:
            user_id = data_set["user_id"]
            if "img" in data_set:
                img_id = data_set["img"]
            else :
                img_id = "https://cdn4.iconfinder.com/data/icons/seo-and-data/500/pencil-gear-128.png"
            if user_id not in result_data:
                result_data[user_id] = 1
                friend_data[user_id] = img_id
            else :
                result_data[user_id] += 1

        del queryString['gender']


    '''
    #합산 시작
    if
    for data_set in mbti_data:
        data_set.
    '''


    response = {'result': 'success', "sort" : "", "resultData" : result_data, "friendData" : friend_data}
    return jsonify(response)

@app.route('/logout')
def logout():

    #[FIXME] 로그아웃 JWT 제거 구현 필요

    return render_template('login.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=8080, debug=True)
