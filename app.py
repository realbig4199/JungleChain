from bson.objectid import ObjectId
from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask.json.provider import JSONProvider
from flask_jwt_extended import *
from flask_jwt_extended.config import config
from jwt.exceptions import ExpiredSignatureError
from datetime import datetime, timedelta
import json
import os
import time
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

UPLOAD_FOLDER = os.getcwd() + '\\static\\upload'  # 절대 파일 경로
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


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
    return render_template('login.html', title='정글 고리')

# 로그인


@app.route('/login', methods=['POST'])
def user_login():
    # 로그인 정보 유효성 확인 코드
    jsonData = json.loads(request.data)

    id_recieve = jsonData.get('id_give')
    pw_recieve = jsonData.get('pw_give')

    # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
    result = db.user.find_one({'user_id': id_recieve, 'user_pw': pw_recieve})

    # 로그인 정보 유효할 시 token 생성 후 client로 전달
    if result is not None:
        # JWT 토큰 생성
        payload = {
            'user_id': id_recieve,
            'exp': datetime.utcnow() + timedelta(hours=60)  # 24시간 로그인 유지
        }
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디 또는 비밀번호가 틀렸습니다.'})

# 회원가입

# ID 중복 체크 확인


# @app.route('/checkId')
# def check_id():
#     id_receive = request.args.get('id_give')
# <<<<<<< HEAD

# =======
#     # 컬렉션 추후 users에서 user로 바꿔야 함.
# >>>>>>> d09a594fe63bddc2065721603c28f5b53febc4c6
#     user = db.user.find_one({'user_id': id_receive})
#     if user:
#         response = {'result': 'failure'}
#     else:
#         response = {'result': 'success'}

#     return jsonify(response)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in set(['png', 'jpg', 'jpeg', 'gif'])


@app.route("/join", methods=["POST"])
def join():
    # 사용자 정보 받아오기
    id_recieve = request.form["id_give"]
    pw_recieve = request.form["pw_give"]
    name_recieve = request.form["name_give"]

    mbti_recieve = request.form["mbti_give"]

    region_recieve = ""
    if "region_give" in request.form:
        region_recieve = request.form["region_give"]
    smoking_recieve = ""
    if "smoking_give" in request.form:
        smoking_recieve = request.form["smoking_give"]
    gender_recieve = ""
    if "gender_give" in request.form:
        gender_recieve = request.form["gender_give"]

    university_recieve = request.form["university_give"]
    major_recieve = request.form["major_give"]

    img_recieve = None
    if "img_give" in request.files:
        img_recieve = request.files['img_give']

    result = db.user.find_one({'id': id_recieve})

    if result is not None:
        return jsonify({'result': 'fail', 'msg': 'ID 중복확인을 해주세요'})
    else:
        if img_recieve:
            if allowed_file(img_recieve.filename):
                db.user.insert_one({
                    'user_id': id_recieve,
                    'user_pw': pw_recieve,
                    'user_name': name_recieve,
                    "mbti": mbti_recieve,
                    "region": region_recieve,
                    "smoking": smoking_recieve,
                    "gender": gender_recieve,
                    "univ": university_recieve,
                    "major": major_recieve,
                    "img": ""
                })

                file = img_recieve
                filename = id_recieve+'.' + \
                    img_recieve.filename.rsplit('.', 1)[1]
                filepathtosave = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepathtosave)
                db.user.update_one({'user_id': id_recieve}, {
                                   '$set': {"img": img_recieve.filename.rsplit('.', 1)[1]}})
                return jsonify({'result': 'success'})
            else:
                return jsonify({'result': 'fail', 'msg': '허용되지 않는 확장자입니다.'})
        else:
            db.user.insert_one({
                'user_id': id_recieve,
                'user_pw': pw_recieve,
                'user_name': name_recieve,
                "mbti": mbti_recieve,
                "region": region_recieve,
                "smoking": smoking_recieve,
                "gender": gender_recieve,
                "univ": university_recieve,
                "major": major_recieve,
                "img": ""
            })
            return jsonify({'result': 'success'})


# 수정 페이지
@app.route('/mod', methods=['GET'])
def mod():
    user_id = request.args.get('id')
    data = db.user.find_one({'user_id': user_id})
    if data:
        # Flask 템플릿에 전달할 데이터 설정
        user_data = {
            'user_id': data['user_id'],
            'user_pw': data['user_pw'],
            'user_name': data['user_name'],
            "mbti": data['mbti'],
            "region": data['region'],
            "smoking": data['smoking'],
            "gender": data['gender'],
            "univ": data['univ'],
            "major": data['major'],
            # "img": data['img']
        }
        mbti_list = list(db.tbl_cd.find(
            {'knd': 'mbti'}, {"code": "1", "cd_nm": "1"}))
        region_list = list(db.tbl_cd.find(
            {'knd': 'region'}, {"code": "1", "cd_nm": "1"}))
        smoking_list = list(db.tbl_cd.find(
            {'knd': 'smoking'}, {"code": "1", "cd_nm": "1"}))
        gender_list = list(db.tbl_cd.find(
            {'knd': 'gender'}, {"code": "1", "cd_nm": "1"}))

        return render_template('modify.html', user_data=user_data, mbti_list=mbti_list, region_list=region_list, smoking_list=smoking_list, gender_list=gender_list)
    else:
        return jsonify({'result': 'failure'})


# 수정하기(수정 후 저장)
@app.route('/mod/data', methods=['POST'])
def mod_data():
    id_recieve = request.form["id_give"]
    pw_recieve = request.form["pw_give"]
    name_recieve = request.form["name_give"]

    mbti_recieve = request.form["mbti_give"]
    region_recieve = request.form["region_give"]
    smoking_recieve = request.form["smoking_give"]
    gender_recieve = request.form["gender_give"]
    university_recieve = request.form["university_give"]
    major_recieve = request.form["major_give"]

    img_recieve = request.files.getlist("files[]")

    if img_recieve:
        first_file = img_recieve[0]  # 첫 번째 파일만 가져옴.
        # 파일 이름을 보안에 적합한 이름으로 변환
        # filename = secure_filename(first_file.filename)
        filename = secure_filename(first_file.filename)
        file_path = '../static/img/' + filename  # 저장할 경로와 파일 이름을 조합
        first_file.save(file_path)  # 파일을 서버에 저장
        img_recieve = filename
        # first_file.save('../static/img/', "된다")  # 파일을 서버에 저장
        img_recieve = filename  # 파일 이름을 img_recieve에 할당
    result = db.user.update_many({'user_id': id_recieve}, {
        '$set': {'user_pw': pw_recieve,
                 'user_name': name_recieve,
                 'mbti': mbti_recieve,
                 'region': region_recieve,
                 'smoking': smoking_recieve,
                 'gender': gender_recieve,
                 'univ': university_recieve,
                 'major': major_recieve,
                 'img': img_recieve
                 }})
    # 유효성 검사
    if result.modified_count == 1:
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'failure'})


# 메인 페이지
@app.route('/find')
def find():
    token_receive = request.cookies.get('mytoken')

    try:
        # token디코딩합니다.
        payload = jwt.decode(token_receive, secret_key, algorithms=['HS256'])
        myuser = db.user.find_one({'user_id': payload['user_id']})
        userinfo = {'user_id': myuser['user_id'],
                    'user_name': myuser['user_name'], 'user_token': token_receive}
        return render_template("main.html", user_id=userinfo['user_id'], user_name=userinfo['user_name'])

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

    mbti_list = list(db.tbl_cd.find(
        {'knd': 'mbti'}, {"code": "1", "cd_nm": "1"}))
    region_list = list(db.tbl_cd.find(
        {'knd': 'region'}, {"code": "1", "cd_nm": "1"}))
    smoking_list = list(db.tbl_cd.find(
        {'knd': 'smoking'}, {"code": "1", "cd_nm": "1"}))
    gender_list = list(db.tbl_cd.find(
        {'knd': 'gender'}, {"code": "1", "cd_nm": "1"}))
    return render_template('signup.html', mbti_list=mbti_list, region_list=region_list, smoking_list=smoking_list, gender_list=gender_list
                           )


'''
* 메인페이지
* Author : 김병철
*
'''
# 메인 페이지


@app.route('/main')
def main():
    user_id = request.args.get('user_id')
    data = db.user.find_one({'user_id': user_id})

    return render_template('main.html', user_name=data['user_name'], user_id=user_id)


@app.route('/main/search', methods=['POST'])
def getNetworkGraph():
    jsonData = json.loads(request.data)

    my_data = db.user.find_one({'user_id': 'jungle'})

    mbti_flag = jsonData.get('mbtiBtn')
    region_flag = jsonData.get('locBtn')
    univ_flag = jsonData.get('schoolBtn')
    major_flag = jsonData.get('majBtn')
    gender_flag = jsonData.get('genBtn')
    smoking_flag = jsonData.get('smkBtn')

    result_data = {}
    friend_data = {}

    queryString = {
        'user_id': {'$ne': 'jungle'}
    }
    if mbti_flag:
        queryString['mbti'] = my_data["mbti"]
        mbti_data = list(db.user.find(queryString))

        for data_set in mbti_data:
            user_id = data_set["user_id"]
            if "img" in data_set:
                img_id = data_set["img"]
            else:
                img_id = "https://cdn4.iconfinder.com/data/icons/seo-and-data/500/pencil-gear-128.png"
            if user_id not in result_data:
                result_data[user_id] = 1
                friend_data[user_id] = img_id
            else:
                result_data[user_id] += 1
        del queryString['mbti']

    if region_flag:
        queryString['region'] = my_data["region"]
        region_data = list(db.user.find(queryString))

        for data_set in region_data:
            user_id = data_set["user_id"]
            if "img" in data_set:
                img_id = data_set["img"]
            else:
                img_id = "https://cdn4.iconfinder.com/data/icons/seo-and-data/500/pencil-gear-128.png"
            if user_id not in result_data:
                result_data[user_id] = 1
                friend_data[user_id] = img_id
            else:
                result_data[user_id] += 1

        del queryString['region']
    if smoking_flag:
        queryString['smoking'] = my_data['smoking']
        smoking_data = list(db.user.find(queryString))

        for data_set in smoking_data:
            user_id = data_set["user_id"]
            if "img" in data_set:
                img_id = data_set["img"]
            else:
                img_id = "https://cdn4.iconfinder.com/data/icons/seo-and-data/500/pencil-gear-128.png"
            if user_id not in result_data:
                result_data[user_id] = 1
                friend_data[user_id] = img_id
            else:
                result_data[user_id] += 1

        del queryString['smoking']

    if univ_flag:
        queryString['univ'] = my_data['univ']
        univ_data = list(db.user.find(queryString))

        for data_set in univ_data:
            user_id = data_set["user_id"]
            if "img" in data_set:
                img_id = data_set["img"]
            else:
                img_id = "https://cdn4.iconfinder.com/data/icons/seo-and-data/500/pencil-gear-128.png"
            if user_id not in result_data:
                result_data[user_id] = 1
                friend_data[user_id] = img_id
            else:
                result_data[user_id] += 1

        del queryString['univ']

    if major_flag:
        queryString['major'] = my_data['major']
        major_data = list(db.user.find(queryString))

        for data_set in major_data:
            user_id = data_set["user_id"]

            if "img" in data_set:
                img_id = data_set["img"]
            else:
                img_id = "https://cdn4.iconfinder.com/data/icons/seo-and-data/500/pencil-gear-128.png"

            if user_id not in result_data:
                result_data[user_id] = 1
                friend_data[user_id] = img_id
            else:
                result_data[user_id] += 1

        del queryString['major']

    if gender_flag:
        queryString['gender'] = my_data['gender']
        gender_data = list(db.user.find(queryString))

        for data_set in gender_data:
            user_id = data_set["user_id"]
            if "img" in data_set:
                img_id = data_set["img"]
            else:
                img_id = "https://cdn4.iconfinder.com/data/icons/seo-and-data/500/pencil-gear-128.png"
            if user_id not in result_data:
                result_data[user_id] = 1
                friend_data[user_id] = img_id
            else:
                result_data[user_id] += 1

        del queryString['gender']

    '''
    #합산 시작
    if
    for data_set in mbti_data:
        data_set.
    '''

    response = {'result': 'success', "sort": "",
                "resultData": result_data, "friendData": friend_data}
    return jsonify(response)


@app.route('/logout')
def logout():

    # [FIXME] 로그아웃 JWT 제거 구현 필요

    return render_template('login.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=8080, debug=True)
