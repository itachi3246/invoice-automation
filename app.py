import os
from flask import Flask,request,make_response,jsonify
from flask_restful import Resource, Api
import json
from flask_cors import CORS
import base64
from document import Document 
import pdfplumber

UPLOAD_FOLDER = r'static'
app = Flask(__name__,static_folder='static')
app.config['UPLOAD_FOLDER'] = 'static'
app.secret_key = 'my unobvious secret key'
CORS(app)

@app.route('/', methods=['POST','GET'])
def index():
    result = {'message': 'Successfull'}
    return make_response(json.dumps(result), 201)

@app.route('/upload', methods=['POST','GET'])
def show():
    query ='Please input the Pdf!'
    try:
        file = request.form['path']
        # print("-------------file",file)
    except:
        file=None
        print("-------------",query)
        return query
    try:
        doc=Document()
        response=doc.identify_doc(file)
        temp=json.dumps(response)
    except:
        temp='Try Again'
    return temp


def main():
    app.run(host="0.0.0.0",port=5023,threaded=True)

if __name__ == "__main__":
    main()