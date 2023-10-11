from flask import Flask, render_template
app = Flask(__name__)

# URL 별로 함수명이 같거나,
# route('/') 등의 주h소가 같으면 안됩니다.


@app.route('/signup')
def home():
    return render_template('signup.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
