from flask import Flask, render_template, url_for, flash
from forms import RegistrationForm, LoginForm

app = Flask(__name__)

app.config['SECRET_KEY'] = '555RTWE666YHH445as33'

posts = [
	{
	'author': 'Lilach Zinger',
	'title': 'Blog Post 1',
	'content': 'First post content',
	'date_posted' : '16April2023'
	}, 
	{
	'author': 'Ram Zinger',
	'title': 'Blog Post 2',
	'content': 'First post content',
	'date_posted' : 'April 17, 2023'	
	}
]


@app.route("/")
def return_html():
	return render_template('base.html')


@app.route("/about")
def about():
	return render_template('about.html', title='hi 1234')


@app.route("/home")
def home():
	return render_template('home.html', posts=posts, show_post=True)



@app.route("/register", methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		return render_template('register.html', title = 'Register', form=form)
	else:
		return render_template('register.html', title = 'Register', form=form)


@app.route("/login")
def login():
	form = LoginForm()
	return render_template('login.html', title = 'Login', form=form)

if __name__ == '__main__':  
	app.run(debug=True)