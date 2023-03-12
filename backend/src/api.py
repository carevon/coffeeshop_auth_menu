import os
import logging
from flask import Flask, request, jsonify, abort, Response
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
!! Running this function will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
@requires_auth('get:drinks')
def drinks(jwt):
    logging.info('Start of get drinks endpoint;')
    print('Start of get drinks execution.')
    result = Drink.query.all()
    print(f'Results: {result}')
    if len(result) == 0:
        abort(Response('Drinks resource were not found', 404))
    drinks = [drink.short() for drink in result]
    return jsonify({'success': True, 'drinks': drinks})


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def drinks_detail(jwt):
    result = Drink.query.order_by(Drink.id).all()
    
    if len(result) == 0:
        abort(Response('Drinks resource were not found', 404))
    drink_details = [drink.long() for drink in result]
    return jsonify({'success': True, 'drinks': drink_details})


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
def create_drinks(jwt):
    print('Start of post drinks execution.')
    # body = request.get_json()
    # print(json.dumps(body))
    new_title = request.json.get('title', None)
    new_recipe = request.json.get('recipe', None)
    search = request.json.get('search', None)
    try:
        if search:
            pass
        else:
            drink = Drink(title=new_title, recipe=json.dumps([new_recipe]))
            drink.insert()
            result = Drink.query.filter(Drink.id == drink.id).one_or_none()
            # test = Drink.query.filter(Drink.id == drink.id).all()
            print(f'Result: {result}')
            if result is None:
                abort(Response('Drink resource were not found', 404))
            else:
                drinks = [drink.long()]
            return jsonify({'success': True, 'drinks': drinks}, 200)
    except Exception as e:
        abort(Response(f'An unexpected error has occurred while posting drink {e}', 422))


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
def update_drinks(jwt, id):
    request_bar = request.get_json()
    try:
        print('Start of patch drink execution')
        drink = Drink.query.filter(Drink.id == id).first()
        if drink is None:
            abort(Response('Drink resource could not been found', 404))
        else:
            print(request_bar.get('title', None))
            drink.title = request_bar.get('title', None)
            print(f'Updated drink: {drink}')
            drink.update()
            drink = [drink.long()]
            return jsonify({'success': True, 'drinks': drink}, 200)
    except Exception as e:
        abort(Response(f'An unexpected error has occurred while patching drink {e}', 422))


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


# Error Handling
'''
Example error handling for unprocessable entity
'''

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

@app.errorhandler(403) 
def missing_permission_route(e): 
    print(f'Missing permission route handling error: {e}')
    response = jsonify({'success': False,
                        'status_code' : 403,
                        'message' : f'Resource could not be authorized because of a missing permission: {e}'})
    response.status_code = 403
    return response

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": f"Resource could not be proccessed: {error}"
    }), 422

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''

@app.errorhandler(404) 
def invalid_route(e): 
    response = jsonify({'success': False, 
                        'status_code' : 404, 
                        'message' : 'Resource not found'})
    response.status_code = 404
    return response

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(401) 
def not_authorized_route(e): 
    print(f'Not authorized route handling error: {e}')
    response = jsonify({'status_code' : 401, 'message' : f'Route could not be authorized: {e}'})
    response.status_code = 401
    return response


if __name__ == "__main__":
    app.debug = True
    app.run()
