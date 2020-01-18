from flask import Flask, flash, jsonify, redirect, render_template, request, session, app, url_for, flash
from bs4 import BeautifulSoup
import requests
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'THISISASOCIETY'
Bootstrap(app)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message="Invalid Email"), Length(max=100)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

def itemDict(item):
    dict = {
        "image_link": item.find('div', class_='pic').find('img')['data-src'],
        "name": item.find('strong').text,
        "shop_name": item.find('div', class_='offer').find('img')['alt'],
        "price": item.find('div', class_='offer').find('a', class_='price').text,
        "link": item.find('div', class_='offer').find('a', class_='price')['href']
    }
    return dict

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method =="GET":
        return render_template('home.html')
    else:
        name = list(request.form.get("name"))
        # match counter to check if words match
        matches = 0
        counter = 0

        # replace spaces with hyphens for url link
        for letter in name:
            if letter == ' ':
                name[counter] = '-'
            counter += 1
        name = ''.join(name)

        source = requests.get(f'https://www.getprice.com.au/buy-best-{name}.htm').text

        name = name.split('-')

        name_length = len(name)
        #compiles source into lxml file
        soup = BeautifulSoup(source, 'lxml')

        # list of items in HTML
        items_source = soup.findAll('div', class_='list-item-compare li-product')

        # list for item dicts to be stored in
        items = []

        # creates an item dictionary for each item and stores it in items = []
        for item in items_source:
            items.append(itemDict(item))

        for item in items:
            # buffer to store item name from items
            item_buffer = list(set(item['name'].split(' ')))
            print(item_buffer)
            matches = 0
            # iterates over every word in item_buffer
            for i in item_buffer:
                # iterates over every word in name
                for j in name:
                    if (i.lower() == j.lower()):
                        matches += 1
            if matches == name_length:
                print('Found a match: ' + item['name'])
                return render_template('lowest.html', item=item)
        return render_template('notfound.html')

@app.route('/about/')
def about():
    items = [dict(name = 'Nintendo Switch', price = 499.99, store = 'JB HI FI')]
    return render_template('about.html', items=items, quantity=len(items))

@app.route('/signup')
def signup():
    form = RegisterForm()

    return render_template('signup.html', form=form)

@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
