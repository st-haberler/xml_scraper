
from flask import (Flask,
                   render_template, 
                   send_from_directory, 
                   request, 
                   jsonify
)



app = Flask(__name__, static_url_path="")

@app.route('/choose_source', methods=['POST'])
def submit():
    query_year = request.form["year-input"]
    query_doc_number = request.form["doc-number-input"]
    query_branch = request.form["branch-input"]

    # TODO: load token_frame from database via doc_handler; 
    # TODO: load .ann file for the given source
    # TODO: return token_frame and .ann file to frontend 
    
    print(f"Number Input: {query_year}, String Input: {query_branch}")
    
    return "Form submitted successfully!"


# TODO: rewrite this function: parameters should be source_type, year, branch, doc_number
@app.route('/get_doc/<string:source>/<int:index>', methods=['GET'])
def get_doc(source:str, index:int): 
    """
    returns a document as token_frame (metadata + list of tokens + list of entities)
    """
    
    if index < 0 or index >= doc.get_doc_count(source):
        abort(404, f"Index {index} is out of bounds for source {source}")
    else:
        doc_data = doc.get_doc_as_token_frame(source, index)
        return jsonify(doc_data)


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)




@app.route('/')
def index():
    return render_template("index.html")


def run_server():
    global doc
    doc = "TEST"
    app.run(debug=True)