from flask import Flask, flash, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
import os
import pytz

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sharetabi.db'
app.config["TEMPLATES_AUTO_RELOAD"] = True # Ensure templates are auto-reloaded

db = SQLAlchemy(app)

# models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(25), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(pytz.timezone('Asia/Tokyo')))

    # 一旦実装しないで置くもの
    # travels = db.relationship('Travel', backref='user', lazy=True)
    # profile_image = db.Column(...)


class Travel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(pytz.timezone('Asia/Tokyo')))
    location = db.Column(db.String(50), nullable=True)
    report = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(pytz.timezone('Asia/Tokyo')))
    
    # 一旦実装しないで置くもの
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # top_picture =db.Column(...) 


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    travel_id = db.Column(db.Integer, db.ForeignKey('travel.id'), nullable=False)


class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    travel_id = db.Column(db.Integer, db.ForeignKey('travel.id'), nullable=False)
    

@app.route("/", methods=["GET"])
def top():
    return render_template("top.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if (request.method == "POST"):
        
        # 記入情報
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')
        
        # 空欄チェック
        if not username:

            return flash('ユーザー名を入力してください', 'warning')

        elif not password:

            return flash('パスワードを入力してください', 'warning')

        elif not confirmation:

            return flash('パスワードをもう一度入力してください', 'warning')
        
        elif not email:
            
            return flash('メールアドレスを入力してください', 'warning')

        # 同じパスワードが入力されているか
        if password != confirmation:

            return flash('パスワードが一致しません', 'warning')

        # パスワードをハッシュ化
        hash = generate_password_hash(password)
        
        # 記入情報を登録する
        try:
            session.add(User(name=username, password=password, email=email))
            flash('登録に成功しました', 'success')
            return redirect('/')

        except:
            flash('ユーザー名がすでに使われているか、メールアドレスが正しくありません')

    else:
        return render_template("register.html")