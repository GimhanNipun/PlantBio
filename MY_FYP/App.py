from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)




@app.route('/Homepage')
def Homepage():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():


    return render_template('results.html')


# Function to read users from a text file
def load_users():
    users = {}
    try:
        with open("users.txt", "r") as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) == 2:
                    username, password = parts
                    users[username] = password
    except FileNotFoundError:
        print("users.txt not found!")
    return users


@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        users = load_users()

        if username in users and users[username] == password:
            return redirect(url_for('Homepage'))
        else:
            message = "Invalid Username or Password. Please try again."

    return render_template('Login.html', message=message)

if __name__ == "__main__":
    app.run(debug=True, port=8000)
