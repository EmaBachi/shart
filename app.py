from flask import Flask, render_template

# Instantiate application object
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')


# Check name of application
if __name__ == "__main__":
    app.secret_key = 'secret123'
    app.run(debug=True)