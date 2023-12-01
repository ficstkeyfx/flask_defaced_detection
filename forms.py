from wtforms import Form, StringField

class URL_FORM(Form):
    url = StringField("URL")