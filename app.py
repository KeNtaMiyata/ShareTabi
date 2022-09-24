from asyncio.windows_events import NULL
from importlib.resources import path
from flask import Flask, flash, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from flask_session import Session # 使わない
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
import os
import pytz

# アップロードされる拡張子の制限
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif'])

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
    icon = db.Column(db.Integer, nullable=False)
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
    user_name = db.Column(db.String(15), nullable=False)
    travel_id = db.Column(db.Integer, db.ForeignKey('travel.id'), nullable=False)


class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    travel_id = db.Column(db.Integer, db.ForeignKey('travel.id'), nullable=False)


# 画像について
def allowed_file(filename):
    # .があるかどうかのチェックと、拡張子の確認
    # OKなら１、だめなら0
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# 以下ルーティングとアクション
    
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
        icon = request.form.get('icon')
        
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
            user = User(name=username, password=generate_password_hash(password), email=email, icon=icon)
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

        # 画像投稿
        file = request.files['image']

        if not title or not date or not location or not report or not file:
            return flash('must provide all information', 'warning')

        travel = Travel(title=title, date=date, location=location, report=report, user_id=user_id)
        db.session.add(travel)
        db.session.commit()

     
        # 画像保存
        if file and allowed_file(file.filename):                
            new_filename = f'{ current_user.id }_{ travel.id }.png' # 強制敵にpng
            path = os.path.join('./static/images/post', new_filename)
            file.save(path)

        return redirect(f"/travels/{ travel.id }")


    else:
        return render_template("new.html")


# 投稿一覧を表示するページ
@app.route("/travels", methods=["GET", "POST"])
@login_required
def travels():
    travels = Travel.query.all() # 全ての投稿

    list = [[]] # いいね数とidを入れるリスト

    for i in range(len(travels)): # いいね数をカウントするループ
        favorites = Favorite.query.filter(Favorite.travel_id == (i + 1)).all()
        favorites_count = len(favorites)
        list.append([favorites_count, i + 1])

    list.sort(reverse = True) # いいね数の降順でソート

    favorites_count1 = list[0][0] # リスト1番目のいいね数
    favorites_count2 = list[1][0]
    favorites_count3 = list[2][0]
    travel_id1 = list[0][1] # リスト1番目のid
    travel_id2 = list[1][1]
    travel_id3 = list[2][1]
    no1 = 1 # リスト1番目の順位
    no2 = 2
    no3 = 3

    if favorites_count2 == favorites_count1: # リスト2番目が1番目と同じいいね数なら同じ順位に
        no2 = no1
    if favorites_count3 == favorites_count2: # リスト3番目が2番目と同じいいね数なら同じ順位に
        no3 = no2

    travel_no1 = Travel.query.get(travel_id1) # リスト1番目の投稿
    travel_no2 = Travel.query.get(travel_id2) # リスト2番目の投稿
    travel_no3 = Travel.query.get(travel_id3) # リスト3番目の投稿
   
    if (request.method == "GET"):
        search = ""
    
    else: # request.method == "POST"
        search = request.form["search"]
    
    return render_template("travels.html", travels=travels, search=search, travel_no1=travel_no1, travel_no2=travel_no2, travel_no3=travel_no3, no1=no1, no2=no2, no3=no3)
    

# 個々の投稿を表示するページ
@app.route("/travels/<int:travel_id>", methods=["GET","POST"])
@login_required
def travel_show(travel_id):
    travel = Travel.query.get(travel_id)
    travel_user = User.query.get(travel.user_id)
    comments = Comment.query.filter(Comment.travel_id == travel_id)
    favorites = Favorite.query.filter(Favorite.travel_id == travel.id).all()
    favorites_count = len(favorites)
    user_favorite = Favorite.query.filter(Favorite.travel_id == travel.id, Favorite.user_id==current_user.id).all()
    user_favorite_count =len(user_favorite)
    return render_template("show_travel.html", current_user=current_user, travel=travel, travel_user=travel_user, comments=comments, favorites_count=favorites_count, user_favorite_count=user_favorite_count)


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
        return redirect(f"/travels/{ travel_id }")  
  

# 削除機能
@login_required
@app.route("/travels/<int:travel_id>/delete", methods=["GET"])
def travel_delete(travel_id):
    travel = Travel.query.get(travel_id)
    comments = Comment.query.filter(Comment.travel_id==travel_id).all()
    favorites = Favorite.query.filter(Comment.travel_id==travel_id).all()
    for comment in comments:
        db.session.delete(comment)
    for favorite in favorites:
        db.session.delete(favorite)
    os.remove(f"./static/images/post/{ travel.user_id }_{ travel.id }.png")
    db.session.delete(travel)
    db.session.commit()

    # 画像削除
    return redirect("/travels")  


# User全員を表示させるページ
@login_required
@app.route("/users", methods=["GET", "POST"])
def users():
    users = User.query.all()
    if (request.method == "GET"):
        search = ""
    
    else: # request.method == "POST"
        search = request.form["search"]

    return render_template("users.html", users=users, search=search)


# Userごとのページ
@login_required
@app.route("/users/<int:user_id>", methods=["GET"])
def user_show(user_id):
    user = User.query.get(user_id)
    travels = Travel.query.filter(Travel.user_id == user.id)
    return render_template("show_user.html", user=user, travels=travels)


# /travels/4/ でコメント送信ボタンを押すとここに来るようにする
@app.route("/travels/<int:travel_id>/comments", methods=["POST"])
@login_required
def comment(travel_id):
    body = request.form.get("body")
    comment = Comment(body=body, user_id=current_user.id, user_name=current_user.name, travel_id=travel_id)
    db.session.add(comment)
    db.session.commit()
    return redirect(f"/travels/{ travel_id }")


# コメント削除
@app.route("/travels/<int:travel_id>/comments/<int:comment_id>/delete", methods=["GET"])
@login_required
def comment_delete(travel_id, comment_id):
    comment = Comment.query.get(comment_id)
    db.session.delete(comment)
    db.session.commit()
    return redirect(f"/travels/{ travel_id }")


# いいね機能
@app.route("/travels/<int:travel_id>/favorites", methods=["GET"])
@login_required
def favorite(travel_id):
    favorite = Favorite.query.filter(Favorite.user_id == current_user.id, Favorite.travel_id == travel_id).all()
    print(favorite)
    if len(favorite) == 0:
        favorite=Favorite(user_id=current_user.id, travel_id=travel_id)
        db.session.add(favorite)
        db.session.commit()

    else:
        favorite = Favorite.query.filter(Favorite.user_id==current_user.id, Favorite.travel_id==travel_id).first()
        db.session.delete(favorite)
        db.session.commit()

    return redirect(f"/travels/{ travel_id }")
