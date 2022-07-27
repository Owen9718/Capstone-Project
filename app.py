from crypt import methods
from sqlite3 import IntegrityError
from flask import Flask, render_template, request, flash, redirect, session
from models import db, connect_db,User,Saved_Recipe
from forms import LoginUser,Search
import requests
from config import headers,secret_api

app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///capstone1"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config["SECRET_KEY"] = "capstone"


connect_db(app)

search_url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/complexSearch"

base_url = 'https://api.spoonacular.com/recipes/'

CURR_USER_KEY = "curr_user"

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


@app.route('/',methods = ["GET","POST"])
def home():
    form = LoginUser()
    if form.validate_on_submit():
        user = User.authenticate(username = form.username.data, password = form.password.data)
        if user:
            do_login(user)
            return redirect('/home')



    return render_template('login.html',form=form)


@app.route('/signup',methods = ["GET","POST"])
# create account
def signup():
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = LoginUser()
    if form.validate_on_submit():
        if User.query.filter(User.username == form.username.data).first():
            flash("Username already taken")
            return render_template('signup.html',form=form)
        else:
            user = User.register(username = form.username.data, password = form.password.data)
            
            db.session.commit()
        
            do_login(user)

            return redirect('/')


    return render_template('signup.html',form=form)



@app.route('/home',methods=['GET','POST'])
def user_home():
    if CURR_USER_KEY in session:
        form = Search()
    
        if form.validate_on_submit():
            querystring = {"query":form.search.data,"number":'5'}
            response = requests.request("GET", search_url,headers=headers,params=querystring).json()
        # print(response)
            print(response)
            return render_template('search.html',form=form,response=response)
        # for results in response['results']:
        #print (results['title'])
        
    
        return render_template('search.html',form=form)
    else:
        return redirect('/')
    


@app.route('/search/<int:recipe_id>', methods=['GET','POST'])
def get_recipe(recipe_id):

    response = requests.request("GET",base_url+str(recipe_id)+f'/information?apiKey={secret_api}').json()
    instructions = requests.request("GET",base_url+str(recipe_id)+f'/analyzedInstructions?apiKey={secret_api}').json()
    if request.method == 'POST':
        user = session[CURR_USER_KEY]
        if Saved_Recipe.query.filter(Saved_Recipe.recipe_id==recipe_id, Saved_Recipe.user_id==user).first():
            return redirect('/home')
        saved = Saved_Recipe(recipe_id=recipe_id,user_id=user,recipe_title=response['title'])
        
        db.session.add(saved)
        db.session.commit()
        return redirect('/home')
    

    return render_template('recipe.html',response=response,instructions=instructions)





@app.route('/saved_recipes',methods=['GET','POST'])
def list_recipes():
    user = session[CURR_USER_KEY]
    if request.method == 'POST':
        recipe = request.form.get('recipe_id')
        delete = Saved_Recipe.query.filter(Saved_Recipe.recipe_id==recipe, Saved_Recipe.user_id==user).first()
        db.session.delete(delete)
        db.session.commit()
        return redirect('/saved_recipes')



    
    save = Saved_Recipe.query.filter(Saved_Recipe.user_id==user).all()
    
    return render_template('saved_recipe.html',recipes=save)


@app.route('/signout')
def signout():
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    
    return redirect('/')