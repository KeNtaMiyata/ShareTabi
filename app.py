from flask import Flask, redirect, render_template, request, session
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


# /travels/4/ でコメント送信ボタンを押すとここに来るようにする
# まだ試していない
@app.route("/travels/<int:travel_id>/comments", methods=["POST","PUT", "DELETE"])
def comment(travel_id):
    if request.method == "POST":
        body = request.form.get("body")
        comment = Comment(body=body, user_id=current_user.id, travel_id=travel_id)
        db.session.add(comment)
        db.session.commit()
        return redirect(f"travels/{ travel_id }")
    
    elif request.method == "PUT":
        comment = Comment.query.filter(Comment.user_id == current_user.id, Comment.travel_id == travel_id).one()
        comment.body=request.form.get("body")
        db.session.add(comment)
        db.session.commit()
        return redirect(f"travels/{ travel_id }")

    else: # request.method == "DELETE":
        comment = Comment.query.filter(Comment.user_id == current_user.id, Comment.travel_id == travel_id).one()
        db.session.delete(comment)
        db.session.commit()
        return redirect(f"travels/{ travel_id }")


@app.route("/travels/<int:travel_id>/favorites", methods=["POST", "DELETE"])
def favorite(travel_id):
    if request.method == "POST":
        favorite=Favorite(user_id=current_user.id, travel_id=travel_id)
        db.session.add(favorite)
        db.session.commit()
        return redirect(f"travels/{ travel_id }")

    else:  # request.method == "DELETE":
        favorite = Favorite.query.filter(Favorite.user_id == current_user.id, Favorite.travel_id == travel_id).one()
        db.session.delete(favorite)
        db.session.commit()
        return redirect(f"travels/{ travel_id }")

