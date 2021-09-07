from flask import Flask, render_template, request, jsonify, g, session, flash, redirect, abort
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm, RegisterForm, UserEditForm, BucketlistForm, SelectBucketlistForm
import requests
import os
from models import db, connect_db, User, Bucketlist, BucketlistCountry

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "secret1273624")
uri = os.environ.get("DATABASE_URL") 
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = (uri, "postgresql:///letsgotravel")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

connect_db(app)

COUNTRIES_API_BASE_URL = "https://restcountries.eu/rest/v2"
PIXABAY_API_BASE_URL = "https://pixabay.com/api/"
PIXABAY_API_KEY = ""

DEFAULT_HEADER_IMG = "/static/images/travel-default.webp"

##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
              

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = RegisterForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError as e:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect(f"/users/{user.id}")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()

    flash("You have successfully logged out.", 'success')
    return redirect("/login")
        
##############################################################################
# General user routes:  
    
@app.route('/users')
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.html', users=users)


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""
    user = User.query.get_or_404(user_id)
    bucketlists = Bucketlist.query.filter_by(user_id=user_id).all()
    return render_template('users/show.html', user=user, bucketlists=bucketlists)


@app.route('/users/profile', methods=["GET", "POST"])
def edit_profile():
    """Update profile for current user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = g.user
    form = UserEditForm(obj=user)

    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):
            user.username = form.username.data
            user.email = form.email.data
            user.image_url = form.image_url.data or "/static/images/default-pic.png"
            user.header_image_url = form.header_image_url.data or DEFAULT_HEADER_IMG
            user.bio = form.bio.data
            user.location = form.location.data

            db.session.commit()
            return redirect(f"/users/{user.id}")

        flash("Wrong password, please try again.", 'danger')

    return render_template('users/edit.html', form=form, user_id=user.id)


@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")


##############################################################################
# Country routes:

def get_country_image(country_name):
    """Call Pixabay API and return country im age url."""
        
    pixabay_params = {'q': f'{country_name}+capital', 
                      'image_type': 'photo', 
                      'category': 'landmark', 
                      'per_page': 3, 
                      'key': PIXABAY_API_KEY}
    
    pixabay_resp = requests.get(PIXABAY_API_BASE_URL, params=pixabay_params)
    data = pixabay_resp.json()
    img_url = data['hits'][0]['largeImageURL']
    
    return img_url or DEFAULT_HEADER_IMG
        

@app.route("/")
def show_country_form():
    """Show country form."""
    return render_template("country_form.html")


@app.route("/country")
def get_country_info():
    """Call country API and show country info page."""
    
    country = request.args["country"]
        
    try:
        country_resp = requests.get(f"{COUNTRIES_API_BASE_URL}/name/{country}")
        country_resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        flash(f"Country not found", 'info')
        return redirect("/")
    
    data = country_resp.json()
    country_record = data[0]
    
    img_url = get_country_image(country)
    
    return render_template("country_info.html", country_record=country_record, img_url=img_url)



@app.route("/bucketlists/<country_name>/add-country", methods=["GET", "POST"])
def add_country_to_playlist(country_name):
    """Add a country and redirect to bucketlist."""
    
    form = SelectBucketlistForm()
    
    result = (db.session.query(Bucketlist.id, Bucketlist.name)
                            .filter_by(user_id=g.user.id)
                            .all())    
    form.bucketlist.choices = [list(i) for i in result]
    
    if form.validate_on_submit():
        
        current_countries = (db.session.query(BucketlistCountry.country_name)
                            .filter_by(bucketlist_id=form.bucketlist.data)
                            .all())
        
        if country_name in [i for i, in current_countries]:
            flash(f"Country {country_name} is already in bucketlist", 'danger')
            return redirect("/")
        
        bucketlist_country = BucketlistCountry(
                country_name=country_name,
                bucketlist_id=form.bucketlist.data
                )
        db.session.add(bucketlist_country)
        db.session.commit()

        flash(f"Country {country_name} added to bucketlist", 'success')
        return redirect("/")

    return render_template("bucketlist/add_country_to_bucketlist.html",
                            country_name=country_name,
                            form=form)

@app.route("/bucketlists/country/<country_name>/complete", methods=["POST"])
def complete_bucketlist_item(country_name):
    """Mark countries as completed and update the database."""
    bucketlist_name = request.json["bucketlist_name"]
    completed = bool(request.json["completed"])
        
    bucketlist = (
        Bucketlist.query
            .filter_by(name=bucketlist_name,user_id=g.user.id)
            .one()
                )
    country_to_complete = (
        BucketlistCountry.query
            .filter_by(bucketlist_id=bucketlist.id 
            ,country_name=country_name)
            .one()
            )
    country_to_complete.completed = completed
    db.session.commit()
    return jsonify(result = 'success')
    
 ##############################################################################
 # Bucketlist routes:
 
@app.route("/bucketlists/<int:bucketlist_id>")
def show_bucketlist(bucketlist_id):
    """Show detail on specific bucketlist."""

    bucketlist = Bucketlist.query.get_or_404(bucketlist_id)
    return render_template("bucketlist/bucketlist.html", bucketlist=bucketlist)   
    

@app.route("/bucketlists/add", methods=["GET", "POST"])
def add_playlist():
    """Handle add-bucketlist form:

    - if form not filled out or invalid: show form
    - if valid: add bucketlist and redirect to user profile page
    """
    form = BucketlistForm()
    
    if form.validate_on_submit(): 
        try:
            new_bucketlist = Bucketlist(
                name=form.name.data,
                description = form.description.data
                )
            g.user.bucketlists.append(new_bucketlist)
            db.session.commit()
            
        except IntegrityError as e:
            db.session.rollback()
            flash(f"Buckelist with name {form.name.data} already exists", 'danger')
            return render_template("bucketlist/new_bucketlist.html", form=form) 
        
        return redirect(f"/users/{g.user.id}")
    else:
        return render_template("bucketlist/new_bucketlist.html", form=form)   


@app.route('/users/<bucketlist_name>/validate')
def validate_user(bucketlist_name):  
    """Check if logged in user has access to edit the bucketlist."""
    bucketlist = (
        Bucketlist.query
            .filter_by(name=bucketlist_name).one()
            )
    if bucketlist.user_id != g.user.id:
        return jsonify(status=403)
    
    return jsonify(status=200)