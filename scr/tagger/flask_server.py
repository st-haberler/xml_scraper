
from flask import (Flask,
                   render_template, 
                   send_from_directory, 
                   request, 
                   jsonify, 
                   abort
)

import doc_db
import doc_handler



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
    document = doc_handler.DocumentHandler()
    query = doc_db.DBQuery(
        source_type=source_type,
        index=index,
        year=year
    )
    token_frame = document.get_token_frame_as_json(query)
    return jsonify(token_frame)



@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)




@app.route('/')
def index():
    return render_template("index.html")



if __name__ == "__main__":
    app.run(debug=True)
