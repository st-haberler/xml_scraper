
from flask import (Flask,
                   render_template, 
                   send_from_directory, 
                   request, 
                   jsonify, 
                   abort
)

import doc_db



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


@app.route("/get_token_frame", methods=["GET"])
def get_token_frame(source_type:str, index:int, year:int=None): 
    database = doc_db.DBCollection()
    query = doc_db.DBQuery(
        source_type=source_type,
        index=index,
        year=year,
        annotation_version=1
    )

    if year is None: 
        return "all good (judikatur)"
    
    return "all good (bundesrecht)"




@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)




@app.route('/')
def index():
    return render_template("index.html")


def run_server():  
    app.run(debug=True)



if __name__ == "__main__":
    run_server()