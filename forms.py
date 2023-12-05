from wtforms import Form, StringField, validators,PasswordField

class URL_FORM(Form):
    url = StringField("URL")

class LoginForm(Form):
    email = StringField("Email", validators=[validators.Length(min=7, max=50), validators.DataRequired(message="Please Fill This Field")])
    password = PasswordField("Password", validators=[validators.DataRequired(message="Please Fill This Field")])