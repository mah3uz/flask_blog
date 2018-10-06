from flask import Flask, render_template, url_for
from forms import RegistrationForm, LoginForm
app = Flask(__name__)

app.config['SECRET_KEY'] = 'b986818991c4870a4d7e449692faeb60'

posts = [
    {
        'title': 'The first post.',
        'author': 'Mahfuz Shaikh',
        'content': 'This is the content of post.',
        'post_date': '04 Sep 2018'
    },
    {
        'title': 'Another post.',
        'author': 'John Doe',
        'content': 'This is the content of another post.',
        'post_date': '12 Aug 2018'
    }
]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts)

@app.route("/post")
def post():
    return render_template('post.html')

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/register")
def register():
    form = RegistrationForm()
    return render_template('register.html', title='Register', form=form)

@app.route("/login")
def login():
    form = LoginForm()
    return render_template('login.html', title='Login', form=form)


if __name__ == '__main__':
    app.run(debug=True)
