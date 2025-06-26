from flask import Flask, render_template, request, redirect, url_for
import sqlite3


app = Flask(__name__)
app.secret_key = 'Khalsa'

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if not username or not email or not password:

            return render_template('signup.html')


        print(f"New user registered: Username - {username}, Email - {email}")

        return redirect(url_for('success'))

    return render_template('signup.html')

@app.route('/success')

def success():
    return render_template('menu.html')

if __name__ == '__main__':
    app.run(debug=True)