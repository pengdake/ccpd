import sys
import os
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
fontC = ImageFont.truetype(os.path.dirname(__file__)+"/font/platech.ttf", 14, 0)
from flask import Flask, render_template, request, make_response, jsonify,abort
from werkzeug import secure_filename
import json
import logging
import base64
import uuid
import HyperLPRLite as pr
import cv2
import numpy as np
import time
import tensorflow as tf
import keras

def drawRectBox(image,rect,addText):
    cv2.rectangle(image, (int(rect[0]), int(rect[1])), (int(rect[0] + rect[2]), int(rect[1] + rect[3])), (0,0, 255), 2,cv2.LINE_AA)
    cv2.rectangle(image, (int(rect[0]-1), int(rect[1])-16), (int(rect[0] + 115), int(rect[1])), (0, 0, 255), -1,
                  cv2.LINE_AA)
    img = Image.fromarray(image)
    draw = ImageDraw.Draw(img)
    draw.text((int(rect[0]+1), int(rect[1]-16)), addText.decode("utf-8"), (255, 255, 255), font=fontC)
    imagex = np.array(img)
    return imagex

def Recognize(imagefile,model_path):
    keras.backend.clear_session()
    graph = tf.get_default_graph()
    grr = cv2.imread(imagefile)
    cascade_path = model_path + "/cascade.xml"
    model12_path = model_path + "/model12.h5"
    #ocr_model_path = model_path + "/ocr_plate_all_gru.h5"
    #ocr_model_path = model_path + "/ocr_plate_all_wrnn.h5"
    #ocr_model_path = model_path + "/ocr_plate_all_w_rnn_2.h5"
    ocr_model_path = model_path + "/ocr_wrnn_ccpd_model.h5"
    model = pr.LPR(cascade_path, model12_path , ocr_model_path)
    for pstr,confidence,rect in model.SimpleRecognizePlateByE2E(grr, graph):
        if confidence>0.7:
            return pstr

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
@app.route('/detect', methods=['POST'])
def upload_file():
    try:
        f = request.files.get('image')
        if not f:
            return make_response('Please provide \'image\' for detectting.\n', 400)
        model_path = app.config.get('model_path')
        basepath = ("/tmp/")
        filename = str(uuid.uuid4()) + '-' + secure_filename(f.filename)
        upload_path = os.path.join(basepath, filename)
        f.save(upload_path)
        res = Recognize(upload_path, model_path)
        if not res:
            return make_response('Result for detecting is null.\n', 400)
        result = {}
        result = {"type": "text"}
        result['data'] = res
        os.remove(upload_path)
        return make_response(jsonify(result), 200)
    except Exception as err:
        logging.error('An error has occurred whilst processing the file: "{0}"'.format(err))
        abort(400)

if __name__ == '__main__':
    app.config['model_path'] = sys.argv[1]
    app.run(debug=False,host="0.0.0.0",port=80)
