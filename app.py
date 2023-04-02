from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_ckeditor import CKEditor
from webforms import LoginForm, PostForm, UserForm, SearchForm

#################### ENV SETUP ##################################################
# activate venv in path [source virt/Scripts/activate]
# view flasker web app  [ export FLASK_ENV=development  or export FLASK_DEBUG=True]
#                       [ export FLASK_APP=hello.py]
#                       [ flask run]

################## GIT UPDATE ###################################################
# INSTRUCTIONS, in virt env, correct dir
# git add .
# git commit -am 'Message'
# git push

###################### INIT & CONFIG  ###########################################
# flask instance
app = Flask(__name__)
#add database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
#secret key
app.config['SECRET_KEY'] = "this is random key goodluck"
#ckeditor init
ckeditor = CKEditor(app)

########################## DATABASE ############################################

db = SQLAlchemy(app)
# migration
migrate = Migrate(app, db, render_as_batch=True)

#Posts model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    date_added = db.Column(db.DATETIME, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    #foreign key
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    date_added = db.Column(db.DATETIME, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    # one to many relation to post
    posts = db.relationship('Posts', backref='poster', lazy=True)

    #Hashing password
    @property
    def password(self):
        raise AttributeError('Password isnt a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

# Creating String
def __repr__(self):
    return '<Name %r>' % self.name

########################## FLASK_LOGIN SETUP ###################################

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

######################### MIGRATE DB ###########################################
# Updates database with migraiton [UPGRADE WHEN DB IS CHANGED]

# >>>>> In GITBASH, virt env on, c/flasker dir

# INSTRUCTIONS >>>>>>>>>>
# pip install Flask-Migrate
# flask db init
# flask db migrate -m 'Initial migration'
# flask db upgrade


###################### FIRST ROUTE PAGES #######################################
# Create route
@app.route('/')
#def index():
#    return "<h1>Hello world!</h1>"
def index():
    return render_template("index.html")

# localhost:5000/user/name
@app.route('/user/<name>')
def user(name):
    return render_template("user.html", user_name=name)
    #return "<h1>Hello {}!</h1>".format(name)

###################################### ROUTES ##################################
#login.html route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login successful")
                return redirect(url_for('dashboard'))
            else:
                flash("Incorrect password")
        else:
            flash("User doesn't exist.")

    return render_template('login.html', form=form)

#logout.html route
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You logged out.")
    return redirect(url_for('login'))

#dashboard.html route
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.username = request.form['username']
        name_to_update.email = request.form['email']
        try:
            db.session.commit()
            flash("USER updated.")
            return render_template("dashboard.html",
                form=form,
                name_to_update = name_to_update)
        except:
            flash("ERROR, user not updated")
            return render_template("dashboard.html",
                form=form,
                name_to_update = name_to_update)
    else:
        return render_template("dashboard.html",
                form=form,
                name_to_update = name_to_update,
                id = id)

# add_user.html route
@app.route('/users/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            #hash pwd
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(username=form.username.data, name=form.name.data, email=form.email.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.username.data = ''
        form.name.data = ''
        form.email.data = ''
        form.password_hash.data = ''
        flash("User added")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html",
        form=form,
        name = name,
        our_users=our_users)
        
# update.html route     [Update user]
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.username = request.form['username']
        name_to_update.email = request.form['email']
        try:
            db.session.commit()
            flash("USER updated.")
            return render_template("update.html",
                form=form,
                name_to_update = name_to_update, 
                id=id)
        except:
            flash("ERROR, user not updated")
            return render_template("update.html",
                form=form,
                name_to_update = name_to_update, 
                id=id)
    else:
        return render_template("update.html",
                form=form,
                name_to_update = name_to_update,
                id=id)

# delete.html route [delete user]
@app.route('/delete/<int:id>')
@login_required
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User deleted")
        
        our_users = Users.query.order_by(Users.date_added)
        return render_template("add_user.html",
        form=form,
        name = name,
        our_users=our_users)
    
    except:
        flash("Error - Deleting user")
        return render_template("add_user.html",
        form=form,
        name = name,
        our_users=our_users)

#admin.html route
@app.route('/admin')
@login_required 
def admin():
    id = current_user.id
    if id == 1:
        return render_template("admin.html")
    else:
        flash("Access Denied, you are not Admin.")
        return redirect(url_for('dashboard'))

# add_post.html route
@app.route('/add-post', methods=['GET', 'POST'])
@login_required 
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title=form.title.data, poster_id=poster, slug=form.slug.data, content=form.content.data)
        form.title.data = ''
        form.slug.data = ''
        form.content.data = ''

        db.session.add(post)
        db.session.commit()
        flash("Post added.")
    return render_template("add_post.html", form=form)


#posts.html     [viewing posts]
@app.route('/posts')
def posts():
    posts = Posts.query.order_by(Posts.date_added.desc())
    return render_template("posts.html", posts=posts)

#post.html      [view a specific post]
@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)

#edit_post.html     [individual edit]
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required 
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.slug = form.slug.data
        post.content = form.content.data
        #update db
        db.session.add(post)
        db.session.commit()
        flash("Post updated")
        return redirect(url_for('post', id=post.id))
    
    if current_user.id == post.poster_id:
        form.title.data = post.title
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template('edit_post.html', form=form)
    else:
        flash("You need authorised access to edit this post.")
        posts = Posts.query.order_by(Posts.date_added)
        return render_template("posts.html", posts=posts)

#delete post
@app.route('/posts/delete/<int:id>')
@login_required 
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster.id or id == 1:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            flash("Blog deleted.")
            posts = Posts.query.order_by(Posts.date_added)
            return render_template("posts.html", posts=posts)
        
        except:
            flash("Error deleting blog")
            posts = Posts.query.order_by(Posts.date_added)
            return render_template("posts.html", posts=posts)
    else:
        flash("You need authorised access to delete this post.")
        posts = Posts.query.order_by(Posts.date_added)
        return render_template("posts.html", posts=posts)

#navbar passer
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

#search.html    [search in navbar]
@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        #get data from form
        post.searched = form.searched.data
        #query db
        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()
        return render_template("search.html", 
        form=form, 
        searched = post.searched,
        posts = posts)
    else:
        flash("nto workinf")

#user_posts.html    [all the users posts]
@app.route('/my-posts')
def myposts():
    posts = Posts.query.order_by(Posts.poster_id)
    postCount = False
    for post in posts:
        if post.poster_id == current_user.id:
            postCount = True
            break
    if postCount == True:
         return render_template("myposts.html", posts=posts)
    else:
        return render_template('noposts.html', posts=posts)
   
#template.html      [template scripts]
@app.route('/template')
def template():
    return render_template("template.html")

##################### Error pages #############################
#Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404 

# Internal error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500
    