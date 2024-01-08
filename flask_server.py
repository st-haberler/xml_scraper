import logging
import logging

from flask import (Flask,
                   request, 
                   render_template, 
                   send_from_directory, 
                   jsonify, 
                   abort
)

import scr.database.db_utils as db_utils 
from scr.database.token_frame import TokenFrame 



logging.basicConfig(level=logging.INFO)
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


@app.route("/get_token_frame")
def get_token_frame(): 
    if request.method == "GET":
        query_dict = request.get_json()
        logging.info(query_dict)
        if (query_dict.get("geschaeftszahl") and 
            (query_dict.get("doc_paragraph_id") is not None)):
            logging.info("GZ and doc_paragraph_id given")
            new_tf = TokenFrame.create_token_frame_from_gz(
                gz=query_dict.get("geschaeftszahl"),
                doc_paragraph_id=query_dict.get("doc_paragraph_id"))
            return jsonify(new_tf)
        if (query_dict.get("gesetzesnummer") and 
            (query_dict.get("doc_paragraph_id") is not None) and
            ((query_dict.get("paragraphennummer") is not None) or 
             ((query_dict.get("artikelnummer")) is not None))):          
            new_tf = TokenFrame.create_token_frame_from_gesetzesnummer(gesetzesnummer=query_dict.get("gesetzesnummer"),
                                                                        paragraphennummer=query_dict.get("paragraphennummer", None),
                                                                        artikelnummer=query_dict.get("artikelnummer", None),
                                                                        doc_paragraph_id=query_dict.get("doc_paragraph_id"))
            return jsonify(new_tf)
        else:
            logging.info("GZ and doc_paragraph_id not given")
            abort(400)
    else:
        abort(405)
    
   


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@app.route('/')
def index():
    return render_template("index.html")



if __name__ == "__main__":
    app.run(debug=True)
