
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, get_token_auth_header, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    try:
        getdrink = Drink.query.all()
        drinks = [drink.short() for drink in getdrink]
        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except:
        abort(404)

'''
implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    # print(jwt)
    try:
        getdrinks = Drink.query.order_by(Drink.id).all()
        drinks = [drink.long() for drink in getdrinks]
        
        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except:
        abort(404)

'''
implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(jwt):

    body = request.get_json()

    title = body.get('title', None)
    recipe = json.dumps(body.get('recipe', None))
    

    print(title)
    print(type(title))
    if title is None and recipe is None:
        abort(400)
    try:
        newdrink = Drink(title=title, recipe=recipe)
        newdrink.insert()
        
        return jsonify({
            'success': True,
            'drinks': [drink.long() for drink in Drink.query.all() ]

        })
    except:
        abort(422)
    

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
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks_detail(jwt, drink_id):
    body = request.get_json()
    title = body.get('title', None)
    recipe = json.dumps(body.get('recipe', None))

    getdrink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if getdrink is None:
        abort(404)

    if title is None and recipe is None:
        abort(403)
    
    getdrink.title = title
    getdrink.recipe = recipe
    getdrink.update()

    # GET THE REMAINING DRINKS
    drinks = Drink.query.order_by(Drink.id).all()
    drinkList = [drink.long() for drink in drinks]
    return jsonify({
        'success': True,
        'drinks': drinkList
    })


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
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('patch:drinks')
def delete_drinks(jwt, drink_id):
    # GET THE DRINK TO BE DELETED
    getdrink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if getdrink is None:
        abort(404)
    getdrink.delete()

    # GET THE REMAINING DRINKS
    drinks = Drink.query.order_by(Drink.id).all()
    drinkList = [drink.long() for drink in drinks]
    return jsonify({
        'success': True,
        'drinks': drinkList
    })

# Error Handling
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
implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(400)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal Server Error'
    }), 500

'''
implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def not_authenticated(auth_error):
    return jsonify({
        "success": False,
        "error": auth_error.status_code,
        "message": auth_error.error
    }), auth_error.status_code