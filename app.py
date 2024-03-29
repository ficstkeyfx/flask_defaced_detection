from flask import Flask, render_template, request, session, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy

from forms import URL_FORM, LoginForm
from detection.detect import Detection
import os
import shutil
from detection.crawl import Crawl
app = Flask(__name__)
app.app_context().push()
app.config['SECRET_KEY'] = '!9m@S-dThyIlW[pHQbN^'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:admin@localhost/auth'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(15), unique=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(256), unique=True)
    status = db.Column(db.Integer)


@app.route("/")
def home():
    return render_template("index.html", detect = 0)

@app.route("/login/", methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate:
        query = User.query.filter_by(email=form.email.data)
        print(query.statement.compile(compile_kwargs={"literal_binds": True}))
        user = query.first()
        if user:
            if user.password == form.password.data:
                session['logged_in'] = True
                session['email'] = user.email 
                session['username'] = user.username
                if user.status >=5 :
                    # user.status = user.status + 1
                    # db.session.commit()
                    # status = 0 if user.status > 5 else (5 - user.status)
                    return redirect(url_for('login', alert=1) )
                else:
                    # user.status = 0
                    # db.session.commit()
                    return redirect(url_for('home'))
            else:
                # user.status = user.status + 1
                # db.session.commit()
                # status = 0 if user.status > 5 else (5 - user.status)
                return redirect(url_for('login', alert=1) )
        else:
            flash('Username or Password Incorrect', "Danger")
            return redirect(url_for('login', alert=1))
    return render_template('login.html', form = form)

@app.route("/register/")
def register():
    return render_template("register.html")

@app.route("/detect/", methods=["POST"])
def detect():
    form = URL_FORM(request.form)
    print(form.url.data)
    url = form.url.data
    if(url != ""):
        crawl = Crawl()
        crawl.crawl_data(url)
        file_name = crawl.filename
        file_path = f"detection/images/{file_name}.png"
        file_path_txt = f"detection/text/{file_name}.txt"
        destination_path = f"static/images/detected/{file_name}.png"
        shutil.copy(file_path, destination_path)
    else:
        file_path = form.path_img.data
        file_path_txt = form.path_txt.data
        file = file_path.split("/")[-1].split("\\")[-1]
        file_name = file[:-4]
        destination_path = f"static/images/detected/{file}"
        shutil.copy(file_path, destination_path)
    print(file_path)
    
    detect_model = Detection() 
    img, txt, result = detect_model.detect([file_path, file_path_txt], "fusion")
    if result == 0:
        return render_template("index.html", detect = 1, image_prob = img, txt_prob = txt, image_path = file_name, url=url)
    else :
        return render_template("index.html", detect = 2, image_prob = img, txt_prob = txt, image_path = file_name, url=url)
    return render_template("index.html")
@app.route('/logout/')
def logout():
    session['logged_in'] = False
    return redirect(url_for('home'))

if __name__=="__main__":
    db.create_all()
    app.run(debug=True, port=8000)