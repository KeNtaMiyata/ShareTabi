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
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # SADeprecationWarning: SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and will be disabled by default in the future.

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


@app.route("/new", methods=["GET", "POST"])
def new():
    """post new article"""

    if (request.method == "POST"):

        title = request.form.get("title")
        date = request.form.get("date")
        location = request.form.get("location")
        report = request.form.get("report")
        created_at = request.form.get("created_at")

        if not title or not date or not location or not report or not created_at:
            return flash('must provide all information', 'warning')

        # db.execute("INSERT INTO people (user_id, name, affiliation, gender, met_date, friendly, active, polite, memo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            # session["user_id"], name, affiliation, gender, date, friendly, active, polite, memo)

        travel = Travel(title=title, date=date, location=location, report=report, created_at=created_at)
        db.session.add(travel)
        db.session.commit()

        return redirect("/")

    else:
        return render_template("new.html")