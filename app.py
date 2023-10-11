
# @app.route('/')
# def hello():
#     return flask.render_template('login.html') 


# import
from flask import Flask, render_template
from flask_jwt_extended import *
from flask_jwt_extended.config import config
from jwt.exceptions import ExpiredSignatureError

# flask객체 생성
app = Flask(__name__)

# JWT 매니저 활성화
jwt = JWTManager(app)

# secret key 세팅
app.config.update(
    DEBUG=True,
    JWT_SECRET_KEY="JUNGLECHAIN",
)

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


if __name__ == 'main': 
app.run(debug=True) 