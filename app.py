import qrcode
import io
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, send_file
import psycopg2
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
app.secret_key = "canteen_secret_key"
CORS(app)

# PostgreSQL connection
def get_db_connection():
    return psycopg2.connect(
        dbname="student_db_data",
        user="postgres",
        password="nandini",
        host="localhost",
        port="5432"
    )

@app.route('/')
def home():
    return render_template('canteen.html')

# Route for the home page
@app.route('/home_page.html')
def home_page():
    return render_template('home_page.html')

@app.route('/nav.html')
def nav():
    return render_template('nav.html')

@app.route('/order.html')
def order():  # Changed from 'orders' to 'order' to match URL path
    return render_template('order.html')

@app.route('/account.html')
def account():
    return render_template('account.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/settings.html')
def settings():
    return render_template('settings.html')

@app.route('/feedback.html')
def feedback():
    return render_template('feedback.html')

@app.route('/todays_special.html')
def todays_special():
    return render_template('todays_special.html')

@app.route('/lunch.html')
def lunch():
    return render_template('lunch.html')

@app.route('/offer.html')
def offer():  # Changed from 'offers' to 'offer' to match URL path
    return render_template('offer.html')

@app.route('/bakery1.html')
def bakery1():
    return render_template('bakery1.html')

@app.route('/bevrages.html')
def bevrages():
    return render_template('bevrages.html')

@app.route('/chat items.html')
def chat_items():
    return render_template('chat items.html')

@app.route('/chinese starter.html')
def chinese_starter():  # Changed from 'chinese_starters' to 'chinese_starter' to match URL path
    return render_template('chinese starter.html')

@app.route('/chinese.html')
def chinese():
    return render_template('chinese.html')

@app.route('/frankie.html')
def frankie():
    return render_template('frankie.html')

@app.route('/items for fast.html')
def items_for_fast():
    return render_template('items for fast.html')

@app.route('/juice.html')
def juice():
    return render_template('juice.html')

@app.route('/just new snacks.html')
def just_new_snacks():
    return render_template('just new snacke.html')  # Note: This might be a typo in template name

@app.route('/sandwiches.html')
def sandwiches():
    return render_template('sandwiches.html')

@app.route('/snacks.html')
def snacks():
    return render_template('snacks.html')

@app.route('/south indian.html')
def south_indian():
    return render_template('south indian.html')

@app.route('/special rice.html')
def special_rice():
    return render_template('special rice.html')

@app.route('/combo.html')
def combo():
    return render_template('combo.html')

@app.route('/quick_bites.html')
def quick_bites():
    return render_template('quick_bites.html')

@app.route('/update-password', methods=['POST'])
def update_password():
    if 'user_id' not in session:
        return jsonify({'message': 'User not logged in'}), 401

    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not all([current_password, new_password]):
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Get current password from database
        cur.execute("SELECT password FROM students WHERE id = %s", (session['user_id'],))
        db_password = cur.fetchone()

        if not db_password:
            return jsonify({'message': 'User not found'}), 404
            
        if db_password[0] != current_password:
            return jsonify({'message': 'Current password is incorrect'}), 400

        # Update password
        cur.execute("UPDATE students SET password = %s WHERE id = %s", 
                   (new_password, session['user_id']))
        conn.commit()

        cur.close()
        conn.close()

        return jsonify({'message': 'Password updated successfully!'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_qr')
def generate_qr():
    amount = request.args.get('amount', '100')
    upi_id = request.args.get('upi_id', 'example@upi')

    qr_data = f"upi://pay?pa={upi_id}&pn=VITCanteen&am={amount}&cu=INR"

    qr_img = qrcode.make(qr_data)
    img_io = io.BytesIO()
    qr_img.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')

@app.route('/register', methods=['POST'])
def register():
    if request.is_json:
        data = request.get_json()
        print(data)  # Debug
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        if not all([name, email, password]):
            return jsonify({'error': 'Missing required fields'}), 400

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            # Check if user already exists
            cur.execute("SELECT * FROM students WHERE email=%s", (email,))
            if cur.fetchone():
                return jsonify({'message': 'User already exists'}), 400

            # Insert new user
            cur.execute("INSERT INTO students (name, email, password) VALUES (%s, %s, %s)", 
                       (name, email, password))
            conn.commit()

            cur.close()
            conn.close()

            return jsonify({'message': 'User registered successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Request must be JSON'}), 400

@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        data = request.get_json()
        print(data)  # Debug
        email = data.get('email')
        password = data.get('password')

        if not all([email, password]):
            return jsonify({'error': 'Missing required fields'}), 400

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("SELECT id, name, email FROM students WHERE email=%s AND password=%s", 
                      (email, password))
            user = cur.fetchone()

            cur.close()
            conn.close()

            if user:
                # Store user info in session
                session['user_id'] = user[0]
                session['user_name'] = user[1]
                session['user_email'] = user[2]
                return jsonify({
                    'message': 'Login successful',
                    'user_id': user[0],
                    'name': user[1],
                    'email': user[2]
                }), 200
            else:
                return jsonify({'message': 'Invalid credentials'}), 401
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Request must be JSON'}), 400
    
@app.route('/delete-account', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        return jsonify({'message': 'User not logged in'}), 401

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Delete user from database
        cur.execute("DELETE FROM students WHERE id = %s", (session['user_id'],))
        conn.commit()

        # Clear session
        session.clear()

        cur.close()
        conn.close()

        return jsonify({'message': 'Account deleted successfully!', 'success': True}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Cart management routes
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if request.is_json:
        data = request.get_json()
        user_id = data.get('user_id')
        item_id = data.get('item_id')
        quantity = data.get('quantity', 1)
        price = data.get('price')
        
        if not all([user_id, item_id, price]):
            return jsonify({'error': 'Missing required fields'}), 400
            
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Check if item already exists in cart
            cur.execute("SELECT id, quantity FROM cart WHERE user_id=%s AND item_id=%s",
                      (user_id, item_id))
            cart_item = cur.fetchone()
            
            if cart_item:
                # Update quantity if item exists
                new_quantity = cart_item[1] + quantity
                cur.execute("UPDATE cart SET quantity=%s WHERE id=%s",
                          (new_quantity, cart_item[0]))
            else:
                # Add new item to cart
                cur.execute("""
                    INSERT INTO cart (user_id, item_id, quantity, price)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, item_id, quantity, price))
                
            conn.commit()
            cur.close()
            conn.close()
            
            return jsonify({'message': 'Item added to cart successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Request must be JSON'}), 400

@app.route('/get_cart', methods=['GET'])
def get_cart():
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
        
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get all items in cart with item details
        cur.execute("""
            SELECT c.id, c.item_id, i.name, c.quantity, c.price, (c.quantity * c.price) as total
            FROM cart c
            JOIN items i ON c.item_id = i.id
            WHERE c.user_id = %s
        """, (user_id,))
        
        cart_items = []
        for row in cur.fetchall():
            cart_items.append({
                'id': row[0],
                'item_id': row[1],
                'name': row[2],
                'quantity': row[3],
                'price': float(row[4]),
                'total': float(row[5])
            })
            
        # Calculate cart total
        cur.execute("""
            SELECT SUM(quantity * price) as cart_total
            FROM cart
            WHERE user_id = %s
        """, (user_id,))
        
        cart_total = cur.fetchone()[0] or 0
        
        cur.close()
        conn.close()
        
        return jsonify({
            'cart_items': cart_items,
            'cart_total': float(cart_total)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/update_cart_item', methods=['PUT'])
def update_cart_item():
    if request.is_json:
        data = request.get_json()
        cart_id = data.get('cart_id')
        quantity = data.get('quantity')
        
        if not all([cart_id, quantity]):
            return jsonify({'error': 'Missing required fields'}), 400
            
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            if int(quantity) <= 0:
                # Delete item if quantity is 0 or less
                cur.execute("DELETE FROM cart WHERE id=%s", (cart_id,))
            else:
                # Update quantity
                cur.execute("UPDATE cart SET quantity=%s WHERE id=%s", (quantity, cart_id))
                
            conn.commit()
            cur.close()
            conn.close()
            
            return jsonify({'message': 'Cart updated successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Request must be JSON'}), 400

@app.route('/delete_cart_item', methods=['DELETE'])
def delete_cart_item():
    cart_id = request.args.get('cart_id')
    
    if not cart_id:
        return jsonify({'error': 'Cart item ID is required'}), 400
        
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("DELETE FROM cart WHERE id=%s", (cart_id,))
        conn.commit()
        
        cur.close()
        conn.close()
        
        return jsonify({'message': 'Item removed from cart'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear_cart', methods=['DELETE'])
def clear_cart():
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
        
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("DELETE FROM cart WHERE user_id=%s", (user_id,))
        conn.commit()
        
        cur.close()
        conn.close()
        
        return jsonify({'message': 'Cart cleared successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Payment processing
@app.route('/process_payment', methods=['POST'])
def process_payment():
    if request.is_json:
        data = request.get_json()
        user_id = data.get('user_id')
        payment_method = data.get('payment_method')
        
        if not all([user_id, payment_method]):
            return jsonify({'error': 'Missing required fields'}), 400
            
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Get cart total
            cur.execute("""
                SELECT SUM(quantity * price) as cart_total
                FROM cart
                WHERE user_id = %s
            """, (user_id,))
            
            cart_total = cur.fetchone()[0]
            
            if not cart_total:
                return jsonify({'error': 'Cart is empty'}), 400
                
            # Create payment record
            payment_date = datetime.now()
            cur.execute("""
                INSERT INTO payments (user_id, amount, payment_date, payment_method)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (user_id, cart_total, payment_date, payment_method))
            
            payment_id = cur.fetchone()[0]
            
            # Get cart items for order details
            cur.execute("""
                SELECT item_id, quantity, price
                FROM cart
                WHERE user_id = %s
            """, (user_id,))
            
            cart_items = cur.fetchall()
            
            # Create order details
            for item in cart_items:
                item_id, quantity, price = item
                cur.execute("""
                    INSERT INTO order_details (payment_id, item_id, quantity, price)
                    VALUES (%s, %s, %s, %s)
                """, (payment_id, item_id, quantity, price))
            
            # Clear the cart
            cur.execute("DELETE FROM cart WHERE user_id=%s", (user_id,))
            
            conn.commit()
            cur.close()
            conn.close()
            
            return jsonify({
                'message': 'Payment processed successfully',
                'payment_id': payment_id,
                'amount': float(cart_total),
                'payment_date': payment_date.strftime('%Y-%m-%d %H:%M:%S')
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Request must be JSON'}), 400

@app.route('/get_payment_history', methods=['GET'])
def get_payment_history():
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
        
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get payment history
        cur.execute("""
            SELECT id, amount, payment_date, payment_method, status
            FROM payments
            WHERE user_id = %s
            ORDER BY payment_date DESC
        """, (user_id,))
        
        payments = []
        for row in cur.fetchall():
            payments.append({
                'id': row[0],
                'amount': float(row[1]),
                'payment_date': row[2].strftime('%Y-%m-%d %H:%M:%S'),
                'payment_method': row[3],
                'status': row[4]
            })
            
        cur.close()
        conn.close()
        
        return jsonify({'payments': payments}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_payment_details', methods=['GET'])
def get_payment_details():
    payment_id = request.args.get('payment_id')
    
    if not payment_id:
        return jsonify({'error': 'Payment ID is required'}), 400
        
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get payment info
        cur.execute("""
            SELECT p.id, p.user_id, p.amount, p.payment_date, p.payment_method, p.status,
                   s.name, s.email
            FROM payments p
            JOIN students s ON p.user_id = s.id
            WHERE p.id = %s
        """, (payment_id,))
        
        payment_row = cur.fetchone()
        
        if not payment_row:
            return jsonify({'error': 'Payment not found'}), 404
            
        payment = {
            'id': payment_row[0],
            'user_id': payment_row[1],
            'amount': float(payment_row[2]),
            'payment_date': payment_row[3].strftime('%Y-%m-%d %H:%M:%S'),
            'payment_method': payment_row[4],
            'status': payment_row[5],
            'user_name': payment_row[6],
            'user_email': payment_row[7]
        }
        
        # Get order details
        cur.execute("""
            SELECT od.id, od.item_id, i.name, od.quantity, od.price,
                   (od.quantity * od.price) as total
            FROM order_details od
            JOIN items i ON od.item_id = i.id
            WHERE od.payment_id = %s
        """, (payment_id,))
        
        items = []
        for row in cur.fetchall():
            items.append({
                'id': row[0],
                'item_id': row[1],
                'name': row[2],
                'quantity': row[3],
                'price': float(row[4]),
                'total': float(row[5])
            })
            
        cur.close()
        conn.close()
        
        return jsonify({
            'payment': payment,
            'items': items
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Admin routes
@app.route('/admin/all_payments', methods=['GET'])
def admin_all_payments():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT p.id, p.user_id, s.name, s.email, p.amount, 
                   p.payment_date, p.payment_method, p.status
            FROM payments p
            JOIN students s ON p.user_id = s.id
            ORDER BY p.payment_date DESC
        """)
        
        payments = []
        for row in cur.fetchall():
            payments.append({
                'id': row[0],
                'user_id': row[1],
                'user_name': row[2],
                'user_email': row[3],
                'amount': float(row[4]),
                'payment_date': row[5].strftime('%Y-%m-%d %H:%M:%S'),
                'payment_method': row[6],
                'status': row[7]
            })
            
        cur.close()
        conn.close()
        
        return jsonify({'payments': payments}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/update_payment_status', methods=['PUT'])
def update_payment_status():
    if request.is_json:
        data = request.get_json()
        payment_id = data.get('payment_id')
        status = data.get('status')
        
        if not all([payment_id, status]):
            return jsonify({'error': 'Missing required fields'}), 400
            
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute("UPDATE payments SET status=%s WHERE id=%s", (status, payment_id))
            conn.commit()
            
            cur.close()
            conn.close()
            
            return jsonify({'message': 'Payment status updated successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Request must be JSON'}), 400

if __name__ == '__main__':
    # Create the tables if they don't exist
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Students table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL
        )
    ''')
    
    # Items table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            price DECIMAL(10, 2) NOT NULL,
            category VARCHAR(50),
            image_url VARCHAR(255)
        )
    ''')
    
    # Cart table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
            item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
            quantity INTEGER NOT NULL DEFAULT 1,
            price DECIMAL(10, 2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Payments table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
            amount DECIMAL(10, 2) NOT NULL,
            payment_date TIMESTAMP NOT NULL,
            payment_method VARCHAR(50) NOT NULL,
            status VARCHAR(20) DEFAULT 'completed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Order details table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS order_details (
            id SERIAL PRIMARY KEY,
            payment_id INTEGER NOT NULL REFERENCES payments(id) ON DELETE CASCADE,
            item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
            quantity INTEGER NOT NULL,
            price DECIMAL(10, 2) NOT NULL
        )
    ''')
    
    conn.commit()
    cur.close()
    conn.close()
    
    app.run(debug=True)