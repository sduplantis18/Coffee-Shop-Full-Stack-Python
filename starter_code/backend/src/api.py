import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

# Set up logging
'''
error_log = FileHandler('error.log')
error_log.setFormatter(Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
error_log.setLevel(logging.INFO)
app.logger.setLevel(logging.INFO)
app.logger.addHandler(error_log)
'''

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    #store all drinks in a drinks variable
    drinks = Drink.query.all()
    total_drinks = len(drinks)
    #throw an error if no drinks are found
    if total_drinks == 0:
        abort(404)

    #loop through the list of drinks and add them to a list
    drink_list = [drink.short() for drink in drinks]
   
    
    return jsonify({
        'success':True,
        'drinks':drink_list
    })

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    #store all drinks in a drinks variable
    drinks = Drink.query.all()
    total_drinks = len(drinks)
    #throw an error if no drinks are found
    if total_drinks == 0:
        abort(404)
    #loop through the list of drinks and add them to a list
    drink_list = [drink.long() for drink in drinks]
    
    return jsonify({
        'success':True,
        'drinks':drink_list
    })
'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_new_drink(jwt):
    
    #get user input for drink name and recipe
    body = request.get_json()
    drink_title = body.get('title', None)
    print(drink_title)
    drink_recipe = body.get('recipe', None)
    print(drink_recipe)
    try:
        #insert the above data into the database and throw an error in case it fails
        drink = Drink(title = drink_title, recipe = json.dumps([drink_recipe]))
        drink.insert()
    except:
        abort(422)
    
    return jsonify ({
        'success': True,
        'drinks': [drink.long()]
    }), 200


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(jwt, id):
    body = request.get_json()
    #store selected drink in the drink variable as an drink.id
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    #get the user input on the selected drink
    drink_title = body.get('title', None)
    print(drink_title)
    drink_recipe = body.get('recipe', None)
    print(drink_recipe)
    try:
        #update the drink record in the db and throw 422 if it fails
        drink = Drink(title = drink_title, recipe = json.dumps(drink_recipe))
        drink.update()
    except:
        abort(422)
    
    return jsonify ({
        'success':True,
        'drinks':[drink.long()]
    }), 200


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
    #store selected drink in the drink variable as an drink.id
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not drink:
        abort(404)

    try:
        #delete the drink record in the db and throw 422 if it fails
        drink = Drink(title = drink_title, recipe = json.dumps(drink_recipe))
        drink.delete()
    except:
        abort(422)
    
    return jsonify ({
        'success':True,
        'delete':id
    }), 200


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "Not Found"
                    }), 404
'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'method not allowed'
    }, 405)

 

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'unauthorized'
    } , 401)  