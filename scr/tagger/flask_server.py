import json
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


@app.route("/get_token_frame", methods=["GET", "POST"])
def get_token_frame(): 
    # TODO: For multiple results for the request, we need a proper return value. 

    if request.method == "POST" or request.method == "GET":
        logging.info(f"from flask_server.py/get_token_frame() {request.method = }")
        query_dict = request.form.to_dict()

        # TODO move this to TokenFrame class
        for supposed_int_index in ["gesetzesnummer", "paragraphnummer", "doc_paragraph_id", "artikelnummer"]:
            if supposed_int_index in query_dict:
                try: 
                    if query_dict[supposed_int_index] == "":
                        logging.info(f"deleting {query_dict[supposed_int_index] = }")
                        del query_dict[supposed_int_index] 
                        continue
                    query_dict[supposed_int_index] = int(query_dict[supposed_int_index])
                except ValueError as e:
                    logging.error(e)
                    abort(400)        
        
        logging.info(f"from flask_server.py/get_token_frame() {query_dict = }")
        try: 
            new_token_frame = TokenFrame.create_token_frame_from_request(query_dict)
            return jsonify(new_token_frame)
        except ValueError as e:
            logging.error(e)
            abort(400)

    else:
        abort(405)


@app.route("/get_labels")
def get_labels():
    version = request.args.get("version")
    logging.info(f"getting all labels of version: {version}") 
    try: 
        serialized_labels = db_utils.get_all_annotion_labels_asdict(version)
        logging.info(f"from flask_server: {serialized_labels = }")
        return jsonify(serialized_labels)
    except ValueError as e:
        logging.error(e)
        abort(400)


@app.route("/get_gesetze", methods=["GET"])
def get_gesetze():
    logging.info(f"getting kurztitel+gesetzesnummer of all documents from BrKons application")
    try: 
        all_gesetze = db_utils.get_all_Gesetze()
        logging.info(f"returning Gesetze Liste from flask_server: {len(all_gesetze) = }")
        # kurztitel_list = [(document.kurztitel, document.gesetzesnummer) for document in all_gesetze]
        kurztitel_list = [{"kurztitel": document.kurztitel, "gesetzesnummer": document.gesetzesnummer} for document in all_gesetze]
        return jsonify(kurztitel_list)
    except ValueError as e:
        logging.error(e)
        abort(400)


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@app.route('/')
def index():
    return render_template("index.html")


app.run(debug=True)


if __name__ == "__main__":
    app.run(debug=True)
