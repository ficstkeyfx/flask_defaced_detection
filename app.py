from flask import Flask, render_template, request, session, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from forms import URL_FORM, LoginForm
from detection.detect import Detection
import os
import shutil
from detection.crawl import Crawl
from datetime import datetime
app = Flask(__name__)
app.app_context().push()
app.config['SECRET_KEY'] = '!9m@S-dThyIlW[pHQbN^'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/auth'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(15), unique=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(256), unique=True)
    status = db.Column(db.Integer)

class Website(db.Model):
    idwebsite = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), unique=True)
    url = db.Column(db.String(500), unique=True)

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ngay = db.Column(db.Date, unique=True)
    lan = db.Column(db.Integer)
    image = db.Column(db.Integer)
    text = db.Column(db.Integer)
    fusion = db.Column(db.Integer)
    idwebsite = db.Column(db.Integer)
lan = 1
temp_date = datetime.now().date()
def scheduled_task():
    global lan
    global temp_date
    
    with app.app_context():
        websites = Website.query.all()
        for web in websites:
            current_date = datetime.now().date()
            if(temp_date != current_date):
                lan = 1
                temp_date = current_date
            if(web.url != ""):
                crawl = Crawl()
                crawl.crawl_data(web.url)
                file_name = crawl.filename
                file_path = f"detection/images/{file_name}.png"
                file_path_txt = f"detection/text/{file_name}.txt"
                destination_path = f"static/images/detected/{file_name}.png"
                shutil.copy(file_path, destination_path)
                detect_model = Detection()
                img, txt, result = detect_model.detect([file_path, file_path_txt], "fusion")
                new_history = History(ngay=current_date, image=img, text=txt, fusion=result, lan=lan, idwebsite=web.idwebsite)
                db.session.add(new_history)
                db.session.commit()
        lan += 1
    print("Completed detection")

scheduler = BackgroundScheduler()
scheduler.add_job(func=scheduled_task, trigger="interval", seconds=100)  # Chạy mỗi 10 giây
scheduler.start()


@app.route("/")
def home():
    return render_template("index.html", detect = 0)

@app.route("/target/")
def target():
    return render_template("detect.html", detect = 0)

@app.route("/website/")
def website():
    websites = Website.query.all()
    return render_template("website.html", websites=websites)

@app.route("/website/add/", methods=["POST"])
def addwebsite():
    # Lấy dữ liệu từ form
    name = request.form['name']
    url = request.form['url']

    new_website = Website(name=name, url=url)

    db.session.add(new_website)
    db.session.commit()
    return redirect(url_for('website'))

@app.route("/website/delete/")
def deletewebsite():
    id = request.args.get('id')
    website = Website.query.get(id)
    if website:
        db.session.delete(website)
        db.session.commit()
    return redirect(url_for('website'))

@app.route("/history/")
def history():
    id = request.args.get('website')
    histories = History.query.filter_by(idwebsite=id).all()
    return render_template("history.html", histories=histories)

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
        return render_template("detect.html", detect = 1, image_prob = img, txt_prob = txt, image_path = file_name, url=url)
    else :
        return render_template("detect.html", detect = 2, image_prob = img, txt_prob = txt, image_path = file_name, url=url)
    return render_template("detect.html")
@app.route('/logout/')
def logout():
    session['logged_in'] = False
    return redirect(url_for('home'))

if __name__=="__main__":
    db.create_all()
    app.run(debug=True, port=8000)