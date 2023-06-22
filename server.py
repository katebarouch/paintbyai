from flask import (Flask, render_template, request, flash, session,
                   redirect, jsonify, url_for)
from model import connect_to_db, db, User, Painting, Paint
import crud
from jinja2 import StrictUndefined
from paint_by_number_maker import create_paint_by_numbers
from shop import get_paint_info
from passlib.hash import argon2
from flask import Flask
from datetime import datetime

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
        db.session.add(user) 
        db.session.commit()
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
        user = session['user_id']
    
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
    medium = request.form.get("medium")
    light = request.form.get("light")
    mood = request.form.get("mood")
    number_colors = int(request.form.get("colors"))

    user = session['user_id']
    painting = Painting(user_id = user)
    db.session.add(painting) 
    db.session.commit()

    prompt = (f" A {light} and {mood} {object} painted with {medium} paints")
    print(prompt)
    
    color_dict = create_paint_by_numbers(prompt, number_colors, painting.painting_id)
    print (color_dict)
    filename1= f'{painting.painting_id}vectorized.svg'
    filename2= f'{painting.painting_id}final.svg'

    painting.vectorized_img = filename1
    painting.final_img = filename2
    painting.prompt = prompt
    painting.media = medium
    db.session.commit()

    painting_id = painting.painting_id

    for color, number in color_dict.items():
        print(color)
        print(number)
        paint = Paint(painting_id = painting_id, paint_id = number, hexcode = color, user_id = user)
        db.session.add(paint)
        db.session.commit()
    

    return redirect(f'/finalproduct/{painting_id}')

@app.route('/gallery')
def view_gallery():
    if 'user_id' in session:
        user = session['user_id']
        paintings = Painting.query.filter(Painting.user_id == user).all()
        return render_template("gallery.html", paintings=paintings)
    else:
        return render_template("no_user.html")

@app.route('/finalproduct/<painting_id>')
def view_product(painting_id):
    painting = Painting.query.filter(Painting.painting_id == painting_id).first()
    filename1 = painting.vectorized_img
    filename2 = painting.final_img
    prompt = painting.prompt

    colors = Paint.query.filter(Paint.painting_id == painting_id).all()
    print(colors)

    color_dict = {}
    color_prompts = [f'What is the English name for color {color.hexcode}? Your response should be in the format of "#hexcode: english name".' for color in colors]
    print(color_prompts)
    responses = get_paint_info(color_prompts)
    print(responses)
    
    for index, color in enumerate(colors):
        hexcode = color.hexcode
        number = color.paint_id
        if index < len(responses):
            common_color_name = responses[index]
            color_dict[hexcode] = f"{number} \n {common_color_name}"
        else:
            print(f"No response found for color: {hexcode}")



    return render_template('finalproduct.html', filename1=filename1, filename2=filename2, prompt = prompt, color_dict = color_dict, painting_id=painting_id)

@app.route('/shop')
def shop():
    
    # chat_gpt_content = f"Make a shopping list (as short as possible) of the {media} paints I need to buy to make the following colors: {hexcode_list}. Include common name of the colors, the minimum paint tubes needed and in what colors, and then the recipe to mix the colors, as needed."

    # paint_info = get_paint_info(chat_gpt_content)

    return render_template("shop.html")

@app.route('/logout')
def logout():
    session.clear()
    flash("You are logged out.") 
    return redirect('/#begin')

if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True, port=3000)