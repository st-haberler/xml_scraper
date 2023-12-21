
from flask import (Flask,
                   request, 
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


@app.route("/get_token_frame", methods=["POST"])
def get_token_frame(): 
    query_dict = request.get_json()
    query = doc_db.DBQuery(
        source_type=query_dict.get("source_type"),
        index=query_dict.get("index"),
        year=query_dict.get("year"),
        annotation_version=query_dict.get("annotation_version"),
        doc_id=query_dict.get("doc_id")
    )
    
    document = doc_handler.DocumentHandler()
    
    token_frame = document.get_token_frame_as_json(query)
    print("success on server side")
    return jsonify(token_frame)



@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)




@app.route('/')
def index():
    return render_template("index.html")



if __name__ == "__main__":
    app.run(debug=True)
