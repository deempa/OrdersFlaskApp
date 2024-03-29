from flask import Flask, jsonify, make_response
from flask import render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import timedelta
from dotenv import load_dotenv
from sqlalchemy.sql import func
from werkzeug.exceptions import NotFound
from prometheus_flask_exporter import PrometheusMetrics
from fluent import sender
import logging

load_dotenv()

db = SQLAlchemy()
app = Flask(__name__) 
metrics = PrometheusMetrics(app)

metrics.info('app_info', 'Application info', version='1.0.3')

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(logging.DEBUG)
    
app.logger.info('NomiNomi App started.')


app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://" + os.getenv("DATABASE_USER") + ":" +\
    os.getenv("DATABASE_PASS") + "@" + os.getenv("DATABASE_HOST") +":3306/" + os.getenv("DATABASE_NAME")
    
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

class orderInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    shipment_date = db.Column(db.DateTime, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False) 
    paid = db.Column(db.String(50), nullable=False)
    delivered = db.Column(db.String(50), nullable=False, default='לא')
    quantity = db.Column(db.Integer, nullable=False, default=1)
    
    def __init__(self, name, phone, address, shipment_date, payment_method, paid, delivered='לא', quantity=1):
        self.name = name
        self.phone = phone
        self.address = address
        self.shipment_date = shipment_date
        self.payment_method = payment_method
        self.paid = paid
        self.delivered = delivered
        self.quantity = quantity
        
with app.app_context():
    db.create_all()
    
headings = ("שם מלא ", "מספר טלפון", "כתובת משלוח", "תאריך משלוח", "דרך תשלום", "האם שולם?", "האם נמסר?", "כמות" , "לעידכון", "למחיקה")

@app.route('/')
def index():
    app.logger.info('Index Page Route')
    return render_template('index.html')

@app.route('/add_new_order', methods=['GET', 'POST'])
def add_new_order():
    if request.method == "GET":
        return render_template('add_new_order.html')
    else: 
        try:
            new_order = orderInfo(request.form['name'], request.form['phone'], request.form['address'],\
                request.form['shipment_date'], request.form['payment_method'], request.form['paid'],\
                request.form['delivered'], request.form['quantity'])
            db.session.add(new_order)
            db.session.commit()
            app.logger.info(f"Added new order with Name: {request.form['name']}")
            return render_template('add_new_order.html', success="True")
        except Exception:
            return render_template('add_new_order.html', success="False")
    
@app.route('/remove_order', methods=['GET', 'POST'])
def remove_order():
    if request.method == "GET":
        try:
            phone = request.args["phone"]
        except Exception as e:
            return render_template('remove_order.html')
        exists = db.session.query(orderInfo.id).filter_by(phone=phone).first() is not None
        if exists:
            order = orderInfo.query.filter_by(phone=phone).first()
            db.session.delete(order)
            db.session.commit()
            app.logger.info(f"Removed order with Phone: {phone}")
            return redirect(url_for('view_all_orders'))
        else:
            # logger.info(f"Removed order with Phone: {order.phone}")
            print("test")
    else: 
        phone = request.form['phone']
        exists = db.session.query(orderInfo.id).filter_by(phone=phone).first() is not None
        if exists:
            order = orderInfo.query.filter_by(phone=phone).first()
            db.session.delete(order)
            db.session.commit()
            app.logger.info(f"Removed order with Phone: {phone}")
            return redirect(url_for('view_all_orders'))
        else:
            app.logger.warning(f"Unsuccesful Remove order operation with Phone: {phone}")
            return render_template('remove_order.html', success="False")
    
@app.route('/is_order_exists', methods=['POST', 'GET'])
def is_order_exists():
    phone = request.form['phone'] if request.method == "POST" else request.args["phone"]
    exists = db.session.query(orderInfo.id).filter_by(phone=phone).first() is not None
    if exists:
        order = db.session.query(orderInfo).filter_by(phone=phone).first()
        order = order.__dict__
        app.logger.info(f"Order is exist.")
        return render_template('update_order.html', is_exists="True", name=order["name"], phone=order["phone"], address=order["address"],\
            shipment_date=order["shipment_date"], payment_method=order["payment_method"], paid=order["paid"], \
            delivered=order["delivered"], quantity=order["quantity"])
    else:
        app.logger.info(f"Order is not exist.")
        return render_template('update_order.html', is_exists="False")
    
         
@app.route('/update_order', methods=['GET', 'POST'])
def update_order():
    if request.method == "GET":
        return render_template('update_order.html')
    else:
        try:
            phone = request.form['phone']
            order = db.session.query(orderInfo).filter(orderInfo.phone == phone).first()
            order.name = request.form['name']
            order.phone = request.form['phone']
            order.address = request.form['address']
            order.shipment_date = request.form['shipment_date']
            order.payment_method = request.form['payment_method']
            order.paid = request.form['paid']
            order.delivered = request.form['delivered']
            order.quantity = request.form['quantity']
            db.session.commit()
            app.logger.info(f"Order update succesfuly with Phone: {phone}")
            return redirect(url_for('view_all_orders')) 
        except NotFound:
            flash("Order not found.")
            app.logger.info(f"Order Not Found.")
        except Exception as e:
            flash(f"An error occurred: {str(e)}")
        
        return redirect(url_for('update_order')) 
    
@app.route('/view_all_orders', methods=['GET'])
def view_all_orders():
    orders = [order.__dict__ for order in db.session.query(orderInfo).all()]
    return render_template('view_all_orders.html', headings=headings, data=orders)

@app.route('/view_all_orders_undelivered', methods=['GET'])
def view_all_orders_undelivered():
    orders = [order.__dict__ for order in db.session.query(orderInfo).filter(orderInfo.delivered == "לא נמסר")]
    return render_template('view_undelivered_orders.html', headings=headings, data=orders)

@app.route('/view_analytics', methods=['GET']) 
def view_revenues():
    query = db.session.query(func.sum(orderInfo.quantity)).filter(orderInfo.delivered == "נמסר")
    total_quantity = query.scalar()
    app.logger.info(f"Total orders delivered: {total_quantity}")
    try:
        revenue = total_quantity * 60 
    except:
        revenue = 0
        total_quantity = 0
    return render_template("view_analytics.html", revenue=revenue, units_sold=total_quantity)

@app.route('/health', methods=['GET'])
def health():
    try:
        orderInfo.query.all()
        data = {'message': 'Done', 'code': 'SUCCESS'}
        return make_response(jsonify(data), 200)
    except Exception as e:
        data = {'message': 'Error connecting to the database', 'code': 'FAILURE'}
        return make_response(jsonify(data), 500)

if __name__ == '__main__':
    app.run()  