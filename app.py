from flask import Flask, render_template, request
from forms import URL_FORM
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/detect/", methods=["POST"])
def detect():
    form = URL_FORM(request.form)
    print(form.url.data)
    return render_template("index.html")

# debud mode running on 8000 port
if __name__=="__main__":
    app.run(debug=True, port=8000)