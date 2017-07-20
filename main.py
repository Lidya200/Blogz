#__author__: "lidya habteselassie"

# date: 07/20/2017
# assignment: Blogz
# collaborated with "Edan Aygoda"
from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:12345@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, content, owner):
        self.title = title
        self.content = content
        self.owner = owner

class User(db.Model):

        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(120), unique=True)
        password = db.Column(db.String(120))
        posts = db.relationship('Blog', backref='owner')

        def __init__(self, username, password):
            self.username = username
            self.password = password
            


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username']=username
            return redirect('/newpost')
        else:

            return render_template('/login.html')

    return render_template('login.html')

@app.before_request
def require_login():
    allowd_routes =['index', 'blog', 'login', 'signup']
    if request.endpoint not in allowd_routes and 'username' not in session:
        return redirect('/login')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        username_error = ''
        existing_username_error = ''
        verify_error = ''

        if len(username)>=120 or len(username)==0:
            username_error = "Please enter a valid username"
            return username_error

        if len(username_error)>0:
            return "Tast"

        if password != verify:
            verify_error = "password does not match, please try again"
            return verify_error


        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username']=username

            return redirect('/')
        else:
            existing_username_error = "username already in use"

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')


@app.route("/blog", methods=["POST", "GET"])
def blog():


    blog_id = request.args.get('id')
    blog_user = request.args.get('username')

    if blog_id:
        blog = Blog.query.filter_by(id=blog_id).first()
        return render_template('blog.html', blog= blog, blog_id=blog_id)

    elif blog_user:
        user_id = User.query.filter_by(username=blog_user).first().id
        posts = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('blog.html', posts=posts)


    else:
        blogs= Blog.query.all()
        return render_template('blog.html', page_name = "blog users!", blogs=blogs)

    
    posts = Blog.query.all()
    return render_template('blog.html', posts= posts)


@app.route('/', methods=['POST', 'GET'])
#def index():
    # owner = User.query.filter_by(username=session['username']).first()
def index():

    users = User.query.all()
    return render_template('index.html', users=users)

    #return render_template('index.html')

@app.route('/newpost', methods=['post', 'get'])
def add():
    post = ""
    new_blog = ""
    title_error = ""
    content_error =""
    if request.method == "POST":
        #blog_id = request.form['id']
        blog_title = request.form['title']
        owner = User.query.filter_by(username=session['username']).first()
        
        if not blog_title:
            title_error = "Please type a title for your blog post"
        elif len(blog_title) > 120:
            title_error = "Your title length exceeds the limit, please shorten your title."

        else:
            blog_content = request.form['content']

            if not blog_content:
                content_error="Please type something for blog body."
            elif len(blog_content)>1000:
                content_error= "Your blog body is more than 1000 words."
            else:

                new_blog = Blog(blog_title, blog_content, owner)
                db.session.add(new_blog)
                db.session.commit()

                blog_id = new_blog.id
       
                return redirect("/blog?id=" + str(blog_id))

    return render_template("newpost.html", post=new_blog, title_error=title_error,content_error=content_error)

@app.route("/singlepost")
def singlepost():
    
    posts = db.session.query(Blog)
    post = ""
    for post in posts:
        post = post
    return render_template("single_post.html", post=post)
if __name__ == '__main__':
    app.run()
