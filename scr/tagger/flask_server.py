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


@app.route("/get_token_frame")
def get_token_frame(): 
    if request.method == "GET":
        query_dict = request.get_json()
        logging.info(query_dict)
        try: 
            new_token_frame = TokenFrame.create_token_frame_from_request(query_dict)
            return jsonify(new_token_frame)
        except ValueError as e:
            logging.error(e)
            abort(400)

    else:
        abort(405)
    
   


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@app.route('/')
def index():
    return render_template("index.html")


app.run(debug=True)


if __name__ == "__main__":
    app.run(debug=True)
