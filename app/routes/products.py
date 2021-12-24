import sys
sys.path.append('../../')
from app import app, db
from app.helpers.execution_id import get_execution_id
from app.models.product_model import Products
from flask import Blueprint, request, jsonify
import json
import threading

# blueprint definition
product_blueprint = Blueprint('product', __name__, url_prefix='/')

lock = threading.Lock()

def query_product(product_id):
    if type(product_id) is int:
        lock.acquire()
        try:
            product = Products.query.filter_by(id=product_id).first()
            return product
        finally:
            lock.release()
    else:
        return None


@app.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    execution_id = get_execution_id()
    try:
        id = int(product_id)
        product = query_product(id)
        if product is not None:
            response_data = {
                'success': True,
                'exe_id':execution_id,
                'product':{
                    'id': product.id,
                    'description': product.description,
                    'cost': product.price,
                    'quantity': product.stock
                }
            }
            return jsonify(response_data), 200
        else:
            return jsonify({
                    'success':False, 
                    'exe_id': execution_id,
                    'message':'product_id not found'}), 404
    except ValueError:
        return jsonify({
                    'success':False, 
                    'exe_id': execution_id,
                    'message':'product_id invalid'}), 400

@app.route('/buy/<product_id>', methods=['POST'])
def buy_product(product_id):
    execution_id = get_execution_id()
    try:
        id = int(product_id)
        data = json.loads(request.data)
        quantity = data.get('quantity')
        credit_card = data.get('credit_card')
        if len(str(credit_card)) == 16:
            # check quantity enough
            product = query_product(id)
            if product is not None:
                if product.stock >= quantity:
                    # successful request
                    # update quantity in db
                    lock.acquire()
                    try:
                        product.stock = product.stock - quantity
                        db.session.commit()
                    finally:
                        lock.release()
                        
                    return jsonify({
                        'success': True,
                        'exe_id': execution_id,
                        'amount': f'{quantity*product.price} deducted from credit card', 
                        }), 200

                else:
                    # not enough quantity
                    return jsonify({
                        'success': False,
                        'exe_id': execution_id,
                        'message': 'not enough stock'
                    }), 404
            else:
                # product not in system
                return jsonify({
                    'success': False,
                    'exe_id': execution_id,
                    'message': 'product_id not found in system'
                }), 404
        else:
            # invalid credit card number
            return jsonify({
                'success': False,
                'exe_id': execution_id,
                'message': 'invalid credit card number'
            }), 400
    except ValueError as e:
        return jsonify({
            'success': False,
            'exe_id': execution_id,
            'message':'invalid product id'
        }), 400


@app.route('/stock/<product_id>/<quantity>', methods=['PUT'])
def update_stock(product_id, quantity):
    execution_id = get_execution_id()
    try:
        id = int(product_id)
        quantity = int(quantity)
        product = query_product(id)
        if product is not None:
            lock.acquire()
            try:
                product.stock = product.stock + quantity
                db.session.commit()
            finally:
                lock.release()

            return jsonify({
                'success': True,
                'exe_id': execution_id,
                'message': 'stock added'    
            }), 200
        else:
            return jsonify({
                'success': False,
                'exe_id': execution_id,
                'message': 'product not found in system'
            }), 404
    except ValueError as e:
        return jsonify({
                'success': False,
                'exe_id': execution_id,
                'message': 'invalid input'
            }), 400