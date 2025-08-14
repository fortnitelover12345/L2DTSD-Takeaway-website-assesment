from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3
import re

app = Flask(__name__)
app.secret_key = 'Khalsa'

email_regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

DATABASE = 'database.db'

# Menu items data structure for search bar
MENU_ITEMS = [
    {
        'id': 1,
        'name': 'Wicked Wings',
        'subtitle': 'Get fired up with our Wicked Wings',
        'price': 12.99,
        'description': 'Bold, crispy chicken wings seasoned with a spicy kick that hits just right. Perfectly cooked to golden perfection, they\'re crunchy on the outside, juicy on the inside, and wickedly addictive. Served hot and ready to devour.',
        'image': '/static/Wicked Wings image-CHATGPT.png',
        'keywords': ['wings', 'spicy', 'crispy', 'bold', 'wicked', 'hot']
    },
    {
        'id': 2,
        'name': 'Kendricks Classic',
        'subtitle': 'Dig into Kendrick\'s Classic',
        'price': 15.50,
        'description': 'A freshly collected chicken breast, half-cooked to lock in juicy tenderness while delivering a lightly crispy finish. It\'s a simple, flavorful bite that captures the essence of farm-fresh comfort with a modern twist.',
        'image': '/static/Kendricks Classic image-CHATGPT v2.png',
        'keywords': ['classic', 'chicken', 'breast', 'juicy', 'crispy', 'comfort', 'fresh']
    },
    {
        'id': 3,
        'name': 'Mini Wingys',
        'subtitle': 'Wings, but make \'em easy.',
        'price': 8.75,
        'description': 'Our Mini Wings deliver all the bold, crave-worthy flavor of classic wings, without the bones. These tender, juicy chicken bites are perfectly seasoned, lightly crisped, and made for dipping. Whether you\'re grabbing a quick snack or adding them to your meal, Mini Wings pack serious flavor in every bite-sized piece.',
        'image': '/static/Mini Wingys image-CHATGPT.png',
        'keywords': ['mini', 'wings', 'boneless', 'tender', 'snack', 'dipping', 'seasoned']
    },
    {
        'id': 4,
        'name': 'Euphoria Feast',
        'subtitle': 'A Flavor Journey from Start to Finish',
        'price': 25.00,
        'description': 'Indulge in the ultimate comfort meal with our Euphoria Feast. This hearty combo includes crispy chicken wings, tender chicken nuggets, golden fries smothered in rich gravy, and a fresh, crisp salad. To top it off, enjoy a creamy sundae that perfectly balances the savory flavors. Ideal for those seeking a satisfying and diverse meal experience.',
        'image': '/static/Euphoria Feast image-CHATGPT.png',
        'keywords': ['feast', 'combo', 'wings', 'nuggets', 'fries', 'salad', 'sundae', 'diverse']
    },
    {
        'id': 5,
        'name': 'Keem\'s Japanese style Jumbo',
        'subtitle': 'Crafted with Precision, Inspired by Tradition.',
        'price': 22.50,
        'description': 'A feast crafted for true flavor seekers. Featuring tender chicken wings, expertly sliced with the precision of a katana\'s blade, each bite delivers a satisfying crunch and savory richness. This jumbo combo brings together a medley of chicken-based delights — from crispy karaage to juicy grilled skewers — all inspired by authentic Japanese street food and curated from local traditions.',
        'image': '/static/Keems Japanese Style Jumbo-CHATGPT.png',
        'keywords': ['japanese', 'jumbo', 'karaage', 'skewers', 'traditional', 'authentic', 'street food']
    }
]

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def search_menu_items(query):
    """Search menu items based on query string"""
    if not query:
        return MENU_ITEMS
    
    query = query.lower().strip()
    results = []
    
    for item in MENU_ITEMS:
        # Search in name, subtitle, description, and keywords
        searchable_text = (
            item['name'].lower() + ' ' +
            item['subtitle'].lower() + ' ' +
            item['description'].lower() + ' ' +
            ' '.join(item['keywords'])
        )
        
        # Check if query matches any part of the searchable text
        if query in searchable_text:
            results.append(item)
    
    return results

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/menu')
def menu():
    # Get search query from URL parameters
    search_query = request.args.get('search', '').strip()
    
    # Filter menu items based on search
    filtered_items = search_menu_items(search_query)
    
    # Get cart items for display
    db = get_db()
    cursor = db.execute("""
        SELECT items.name, items.price, items.image_url
        FROM cart
        JOIN items ON cart.item_id = items.item_id
    """)
    cart_items = cursor.fetchall()
    
    return render_template('menu.html', 
                         menu_items=filtered_items, 
                         cart_items=cart_items,
                         search_query=search_query)

email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$"
allowed_domains = ['gmail.com', 'outlook.com', 'yahoo.com', 'hotmail.com', 'edu.nz', 'stu.school.nz']

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        # Ensure all fields are filled
        if not username or not email or not password:
            return render_template('signup.html', error="All fields are required.")

        # Enforce lowercase usernames
        if username != username.lower():
            return render_template('signup.html', error="Username must be in lowercase.")

        # Validate username format (letters, numbers, underscores, hyphens only)
        if not re.fullmatch(r'^[a-z0-9_-]{3,20}$', username):
            return render_template('signup.html', error="Username must be 3-20 characters long and can only contain lowercase letters, numbers, underscores, and hyphens.")

        # Validate email format
        if not re.fullmatch(email_regex, email):
            return render_template('signup.html', error="Invalid email format.")

        # Validate email domain
        domain = email.split('@')[-1]
        if domain.lower() not in allowed_domains:
            return render_template('signup.html', error="Unsupported email domain.")

        # Validate password length and complexity
        if len(password) < 8:
            return render_template('signup.html', error="Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', password):
            return render_template('signup.html', error="Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', password):
            return render_template('signup.html', error="Password must contain at least one lowercase letter.")
        if not re.search(r'[0-9]', password):
            return render_template('signup.html', error="Password must contain at least one number.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return render_template('signup.html', error="Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>).")

        # Proceed with registration (e.g., insert into database)
        print(f"User registered: {username} ({email})")
        return redirect(url_for('menu'))

    return render_template('signup.html')

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    item_id = request.form.get('item_id')
    if item_id:
        db = get_db()
        cursor = db.execute("SELECT quantity FROM cart WHERE item_id = ?", (item_id,))
        row = cursor.fetchone()
        if row:
            db.execute("UPDATE cart SET quantity = quantity + 1 WHERE item_id = ?", (item_id,))
        else:
            db.execute("INSERT INTO cart (item_id, quantity) VALUES (?, 1)", (item_id,))
        db.commit()
    
    # Preserve search query when adding to cart
    search_query = request.form.get('search_query', '')
    return redirect(url_for('menu', search=search_query))

@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    db = get_db()
    db.execute("DELETE FROM cart")
    db.commit()
    return redirect(url_for('checkout'))

@app.route('/checkout')
def checkout():
    db = get_db()
    cursor = db.execute("""
        SELECT items.name, items.price, items.image_url, cart.quantity,
               (items.price * cart.quantity) AS total_price
        FROM cart
        JOIN items ON cart.item_id = items.item_id
    """)
    cart_items = cursor.fetchall()
    total_price = sum(float(item['total_price']) for item in cart_items)
    return render_template('checkout.html', cart_items=cart_items, total_price=total_price)

if __name__ == '__main__':
    app.run(debug=True)