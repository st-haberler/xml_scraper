
from flask import (Flask,
                   render_template, 
                   send_from_directory, 
                   request
)



app = Flask(__name__, static_url_path="")

@app.route('/choose_source', methods=['POST'])
def submit():
    number_input = request.form["year-input"]
    string_input = request.form["branch-input"]
    
    # Process the data as needed, e.g., print or use in your application logic
    print(f"Number Input: {number_input}, String Input: {string_input}")
    
    # Add your own logic here

    return "Form submitted successfully!"



@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)



# route for index page
@app.route('/')
def index():
    return render_template("index.html")


def run_server():
    global doc
    doc = "TEST"
    app.run(debug=True)