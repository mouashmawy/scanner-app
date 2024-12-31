from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model
class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(100), unique=True, nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Inventory {self.product_name}>'

# Check and Create Tables if Not Exist
with app.app_context():
    db.create_all()

@app.route('/add_item', methods=['POST'])
def add_item():
    data = request.json
    barcode = data.get('barcode')
    product_name = data.get('product_name')
    quantity = data.get('quantity', 0)

    # Check if the item already exists
    existing_item = Inventory.query.filter_by(barcode=barcode).first()
    if existing_item:
        return jsonify({"success": False, "message": "Item already exists!"}), 400

    # Add the new item to the database
    new_item = Inventory(barcode=barcode, product_name=product_name, quantity=quantity)
    db.session.add(new_item)
    db.session.commit()

    return jsonify({"success": True, "message": "Item added successfully!"})


@app.route('/add_item_page')
def add_item_page():
    return render_template('add_item.html')


# API Endpoint to Update Inventory
@app.route('/update_inventory', methods=['POST'])
def update_inventory():
    data = request.json
    barcode = data.get('barcode')
    action = data.get('action')  # 'add' or 'remove'

    item = Inventory.query.filter_by(barcode=barcode).first()
    if not item:
        return jsonify({"message": "Item not found!"}), 404

    if action == 'add':
        item.quantity += 1
    elif action == 'remove':
        if item.quantity > 0:
            item.quantity -= 1
        else:
            return jsonify({"message": "Stock already at zero!"}), 400

    db.session.commit()
    return jsonify({"message": "Inventory .updated successfully!", "item": {
        "barcode": item.barcode,
        "product_name": item.product_name,
        "quantity": item.quantity
    }})




@app.route('/get_items', methods=['GET'])
def get_items():
    items = Inventory.query.all()
    items_list = [
        {
            "barcode": item.barcode,
            "product_name": item.product_name,
            "quantity": item.quantity
        }
        for item in items
    ]
    return jsonify(items_list)


@app.route('/all_items')
def all_items():
    return render_template('all_items.html')





# Serve Frontend
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
