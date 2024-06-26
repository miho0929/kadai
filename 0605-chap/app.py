from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import random
from database import init_db, save_result, get_all_results, User, db
from wikipedia_api import get_wikipedia_summary
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///results.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# データベースファイルが存在する場合は削除
if os.path.exists('results.db'):
    os.remove('results.db')

with app.app_context():
    init_db()

shachi_data = {
    'ラビー': ('鴨川シーワールド', 'rabby', 'rabby.jpg'),
    'ララ': ('鴨川シーワールド', 'lala', 'lala.jpg'),
    'ルーナ': ('鴨川シーワールド', 'luna', 'luna.jpg'),
    'アース': ('名古屋港水族館', 'earth', 'earth.jpg'),
    'リン': ('名古屋港水族館', 'rin', 'rin.jpg'),
    'ステラ': ('神戸須磨シーワールド', 'stella', 'stella.jpg'),
    'ラン': ('神戸須磨シーワールド', 'ran', 'ran.jpg')
}

@app.route('/')
def index():
    if current_user.is_authenticated:
        shachi_name = random.choice(list(shachi_data.keys()))
        shachi_image = f'{shachi_data[shachi_name][1]}.jpg'
        return render_template('index.html', shachi_image=shachi_image, shachi_name=shachi_name)
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/result', methods=['POST'])
@login_required
def result():
    guessed_name = request.form['name']
    guessed_aquarium = request.form['aquarium']
    correct_name = request.form['correct_name']
    correct_aquarium = shachi_data[correct_name][0]

    name_result = (guessed_name == correct_name)
    aquarium_result = (guessed_aquarium == correct_aquarium)

    save_result(current_user.username, correct_name, correct_aquarium, guessed_name, guessed_aquarium, name_result, aquarium_result)

    shachi_summary = get_wikipedia_summary(correct_name)

    return render_template('result.html', 
                           name_result=name_result, 
                           aquarium_result=aquarium_result, 
                           correct_name=correct_name, 
                           correct_aquarium=correct_aquarium,
                           shachi_summary=shachi_summary)

@app.route('/history')
@login_required
def history():
    results = get_all_results(current_user.username)
    return render_template('history.html', results=results)

@app.route('/shachi_dict')
def shachi_dict():
    return render_template('shachi_dict.html', shachis=shachi_data.keys())

@app.route('/shachi_info/<name>')
def shachi_info(name):
    if name in shachi_data:
        shachi_summary = get_wikipedia_summary(name)
        shachi_image = shachi_data[name][2]
        return render_template('shachi_info.html', name=name, summary=shachi_summary, shachi_image=shachi_image)
    else:
        return "シャチの情報が見つかりませんでした。"

@app.route('/ranking')
def ranking():
    results = get_ranking()
    return render_template('ranking.html', results=results)

def get_ranking():
    conn = sqlite3.connect('results.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT username, COUNT(*) as score
                      FROM results
                      WHERE name_result = 1 AND aquarium_result = 1
                      GROUP BY username
                      ORDER BY score DESC
                      LIMIT 10''')
    results = cursor.fetchall()
    conn.close()
    return results

if __name__ == '__main__':
    app.run(debug=True)
