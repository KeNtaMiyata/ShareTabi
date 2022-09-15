from flask import Flask, flash, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from flask_session import Session # 使わない
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
import os
import pytz

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sharetabi.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True # ログ出力
           
# シークレットキーの設定。セッション情報を暗号化するための設定。
app.config['SECRET_KEY'] = os.urandom(24)
app.config["TEMPLATES_AUTO_RELOAD"] = True # Ensure templates are auto-reloaded
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # SADeprecationWarning: SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and will be disabled by default in the future.

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

# models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(25), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(pytz.timezone('Asia/Tokyo')))
    travels = db.relationship('Travel', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)
    favorites = db.relationship('Favorite', backref='user', lazy=True)


class Travel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(pytz.timezone('Asia/Tokyo')))
    location = db.Column(db.String(50), nullable=True)
    report = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(pytz.timezone('Asia/Tokyo')))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='travel', lazy=True)
    favorites = db.relationship('Favorite', backref='travel', lazy=True)
    

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    travel_id = db.Column(db.Integer, db.ForeignKey('travel.id'), nullable=False)


class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    travel_id = db.Column(db.Integer, db.ForeignKey('travel.id'), nullable=False)

    
# @login_required : ログイン後のみ付けたい機能だけ
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/", methods=["GET"])
def top():
    return render_template("top.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """ユーザログイン"""
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or  not password:
            flash('ユーザー名またはパスワードを入力してください', 'warning')
            return render_template("login.html")
        
        # usernameが一致するもの
        user = User.query.filter_by(name=username).first()
        
        # ユーザー名が存在し、パスワードが正しいことの確認
        if not user or not check_password_hash(user.password, password):
            flash('ユーザ名またはパスワードが間違っています', 'warning')
            return render_template("login.html")
            
        else:
            login_user(user)
            return redirect("/")
        
    else:
        return render_template("login.html")
 
    
@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
        
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        
        # 記入情報
        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')
        email = request.form.get('email')
        
        # 空欄チェック
        if not username:

            flash('ユーザー名を入力してください', 'warning')
            return render_template("register.html")
        
        elif not email:
            
            flash('メールアドレスを入力してください', 'warning')
            return render_template("register.html")

        elif not password:

            flash('パスワードを入力してください', 'warning')
            return render_template("register.html")
 

        elif not confirmation:

            flash('パスワードをもう一度入力してください', 'warning')
            return render_template("register.html") 

        # 同じパスワードが入力されているか
        if password != confirmation:

            flash('パスワードが一致しません', 'warning')
            return render_template("register.html")
 
        # 同じ名前が使用されているかどうか
        try :
            user_check = User.query.filter_by(name=username).one()
            flash('すでにそのユーザ名は使われています', 'warning')
            return render_template("register.html")
            
        except:
            # 記入情報を登録する
            user = User(name=username, password=generate_password_hash(password), email=email)
            db.session.add(user)
            db.session.commit()
            
            return redirect('/login')
        
    else:
        return render_template("register.html")
 

@app.route("/new", methods=["GET", "POST"])
@login_required
def new():
    """post new article"""

    if (request.method == "POST"):

        title = request.form.get("title")
        date = datetime.datetime.strptime(request.form.get("date"), '%Y-%m-%d')
        location = request.form.get("location")
        report = request.form.get("report")
        user_id = current_user.id

        if not title or not date or not location or not report:
            return flash('must provide all information', 'warning')

        travel = Travel(title=title, date=date, location=location, report=report, user_id=user_id)
        db.session.add(travel)
        db.session.commit()

        return redirect("/")

    else:
        return render_template("new.html")


# 投稿一覧を表示するページ
@app.route("/travels", methods=["GET"])
@login_required
def travels():
    # if (request.method == "GET"):
    travels = Travel.query.all()
    return render_template("travels.html", travels=travels)


# 個々の投稿を表示するページ
@app.route("/travels/<int:travel_id>", methods=["GET","POST"])
@login_required
def travel(travel_id):
    travel = Travel.query.get(travel_id)
    return render_template("show_travel.html", user=current_user, travel=travel)


# 編集画面
@app.route("/travels/<int:travel_id>/edit", methods=["GET","POST"])
@login_required
def travel_edit(travel_id):
    if (request.method == "GET"):  # 表示
        travel = Travel.query.get(travel_id)
        return render_template("edit_travel.html", travel=travel)
        
    else: # request.method == "POST"
        travel = Travel.query.get(travel_id)

        title = request.form.get("title")
        date = datetime.datetime.strptime(request.form.get("date"), '%Y-%m-%d')
        location = request.form.get("location")
        report = request.form.get("report")
        
        if not title or not date or not location or not report:
            return flash('must provide all information', 'warning')

        travel.title=title
        travel.date=date
        travel.location=location
        travel.report=report

        db.session.commit()

        return redirect(f"/travels/{{ travel_id }}")  
  

# 削除機能
@login_required
@app.route("/travels/<int:travel_id>/delete", methods=["GET"])
def travel_delete(travel_id):
    travel = Travel.query.get(travel_id)
    db.session.delete(travel)
    db.session.commit()
    return redirect(f"/travels/{{ travel_id }}")  


# User ごとのページ


# /travels/4/ でコメント送信ボタンを押すとここに来るようにする
@app.route("/travels/<int:travel_id>/comments", methods=["POST"])
@login_required
def comment(travel_id):
    body = request.form.get("body")
    comment = Comment(body=body, user_id=current_user.id, travel_id=travel_id)
    db.session.add(comment)
    db.session.commit()
    return redirect(f"travels/{ travel_id }")


# コメント削除
@app.route("/travels/<int:travel_id>/comments/<int:comment_id>/delete", methods=["POST"])
@login_required
def comment(travel_id, comment_id):
    comment = Comment.query.get(comment_id)
    db.session.delete(comment)
    db.session.commit()
    return redirect(f"travels/{ travel_id }")


# いいね機能
@app.route("/travels/<int:travel_id>/favorites", methods=["POST"])
@login_required
def favorite(travel_id):
    favorite=Favorite(user_id=current_user.id, travel_id=travel_id)
    db.session.add(favorite)
    db.session.commit()
    return redirect(f"travels/{ travel_id }")


# いいね削除
@app.route("/travels/<int:travel_id>/favorites/delete", methods=["POST"])
@login_required
def favorite_cancel(travel_id):
    favorite = Favorite.query.filter(Favorite.user_id == current_user.id, Favorite.travel_id == travel_id).one()
    db.session.delete(favorite)
    db.session.commit()
    return redirect(f"travels/{ travel_id }")

