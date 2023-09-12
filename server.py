from flask import (Flask, render_template, request, flash, session,
                   redirect, jsonify, url_for)
from model import connect_to_db, db, User, Painting, Paint
import crud
from jinja2 import StrictUndefined
import paint_by_number_maker
from shop import get_paint_info, send_message
from passlib.hash import argon2
from flask import Flask
from datetime import datetime
import dalle_img_maker

app = Flask(__name__)
app.secret_key = "dev"
app.jinja_env.undefined = StrictUndefined

# Store the current month and the number of uses
current_month = datetime.now().month
use_count = 0
max_uses = 50


@app.route('/')
def homepage():
    """Show Homepage"""
    return render_template("homepage.html")

@app.route('/faq')
def faq():
    """Show FAQs"""
    return render_template("faq.html")

@app.route('/users', methods=['POST'])
def create_user():
    """Create a new user."""
    email = request.form.get("email")
    password = request.form.get("password")
    hashed = argon2.hash(password)

    user = crud.get_user_by_email(email)
    if user:
        flash("This email is already associated with an account, please login with password.") 
    else:
        user = crud.create_user(email, hashed)
        flash("Account created successfully, and you can now login.")
    return redirect('/#begin')

@app.route('/login', methods=['POST'])
def login():
    """Login user"""
    email = request.form.get("email")
    password = request.form.get("password")
    user = crud.get_user_by_email(email)

    if user:
        if argon2.verify(password, user.password):
            session['user_id'] = user.user_id
            flash('Logged in!')
            return redirect('/create')
        else:
            flash("Wrong Password")
            return redirect(url_for('homepage') + '#begin')
    else:
        flash("Wrong username.")
        return redirect(url_for('homepage') + '#begin')

@app.route('/create')
def create():

    if 'user_id' in session:
    
        global  use_count, current_month

        # Check if the current month has changed
        if datetime.now().month != current_month:
            # Reset the use count for the new month
            current_month = datetime.now().month
            use_count = 0

        if use_count < max_uses:
            # Increment the use count
            use_count += 1
            return render_template("create.html")
        else:
            # Access limit reached, return an error or redirect to another page
            return "Access limit reached for this month."
    
    else:

        return render_template("no_user.html")
    

@app.route('/create', methods = ['POST'])
def get_info():

    object = request.form.get("object")
    media = request.form.get("medium")
    light = request.form.get("light")
    mood = request.form.get("mood")
    number_colors = int(request.form.get("colors"))

    #create prompt
    prompt = (f" A {light} and {mood} {object} painted with {media} paints")
    print(prompt)

    # create painting in database
    user = session['user_id']
    painting = crud.create_painting(user, media, prompt)
    
    painting_id = painting.painting_id

    #call on python algorithms to generate images
    img_path = dalle_img_maker.make_dalle_img(prompt, painting_id)
    color_dict = paint_by_number_maker.create_paint_by_numbers(img_path, number_colors, painting_id)

    # add new images to database
    painting.vectorized_img = f'{painting_id}vectorized.svg'
    painting.final_img = f'{painting_id}final.svg'
    db.session.commit()

    # add paints to database
    for color, number in color_dict.items():
        paint = crud.create_paint(painting_id, number, color, user)

    return redirect(f'/finalproduct/{painting_id}')

@app.route('/gallery')
def view_gallery():
    # view gallery specific to user
    if 'user_id' in session:
        user = session['user_id']
        paintings = Painting.query.filter(Painting.user_id == user).all()
        return render_template("gallery.html", paintings=paintings)
    else:
        return render_template("no_user.html")

@app.route('/finalproduct/<painting_id>')
def view_product(painting_id):
    
    #pull up painting info
    painting = Painting.query.filter(Painting.painting_id == painting_id).first()
    filename1 = painting.vectorized_img
    filename2 = painting.final_img
    prompt = painting.prompt

    colors = Paint.query.filter(Paint.painting_id == painting_id).all()

    # recreate color_dict
    color_dict = {}
    for color in colors:
        hexcode = color.hexcode
        number = color.paint_id
        color_dict[hexcode] = number


    return render_template('finalproduct.html', filename1=filename1, filename2=filename2, prompt = prompt, color_dict = color_dict, painting_id=painting_id)

@app.route('/shop')
def shop():

    return render_template("shop.html")

@app.route('/logout')
def logout():
    session.clear()
    flash("You are logged out.") 
    return redirect('/#begin')

if __name__ == "__main__":
    connect_to_db(app)
    app.run(port=5000)
