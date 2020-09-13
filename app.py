import os, base64
from flask import Flask, render_template, request, redirect, flash

import json
from IPython.display import HTML

from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import asyncio
import io
import glob
import os
import sys
import time
import uuid
import requests
from urllib.parse import urlparse
from io import BytesIO
from PIL import Image, ImageDraw, ImageFilter
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person, SnapshotObjectType, OperationStatusType

app = Flask(__name__)

# Set the FACE_SUBSCRIPTION_KEY environment variable with your key as the value.
# This key will serve all examples in this document.
KEY = os.environ['FACE_SUBSCRIPTION_KEY']

UPLOAD_FOLDER = "static"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set the FACE_ENDPOINT environment variable with the endpoint from your Face service in Azure.
# This endpoint will be used in all examples in this quickstart.
ENDPOINT = os.environ['FACE_ENDPOINT']
face_credentials = CognitiveServicesCredentials(KEY)
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Prevent caching
@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
      
    return r

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Display the image that was uploaded
        image = request.files["file"]
        uri = "data:image/jpg;base64," + base64.b64encode(image.read()).decode("utf-8")
        #image.save(os.path.join("static", image.filename));
        image.seek(0)

        # Use the Computer Vision API to extract text from the image
        blur_faces(image, face_client)
        uri = "/static/out.jpg"

    else:
        # Display a placeholder image
        uri = "/static/placeholder.png"

    return render_template("index.html", image_uri=uri)

@app.route('/blur_pic', methods=["GET", "POST"])
def blur_pic():
    print ("Hello")
              
    uri = "/static/placeholder.png"      
    return render_template("index.html", image_uri=uri)
    
    
# Function that extracts text from images
def blur_faces(image, client):
    detected_faces = client.face.detect_with_stream(image=image)
    if not detected_faces:
        print("No faces found in image")
        return
    else:
        for face in detected_faces:
            print(face.face_id)
            
    response = request.files["file"]
    img = Image.open(response)
    
    # Create mask
    mask = Image.new('L', img.size, 0)
    
    drawMask = ImageDraw.Draw(mask)
    
    for face in detected_faces:
        drawMask.ellipse(getPoints(face), fill=255, outline='red')
    
    mask.save('static/mask.png')  

    # Blur image
    blurred = img.filter(ImageFilter.GaussianBlur(10))

    # Paste blurred region and save result
    img.paste(blurred, mask=mask)
    
    #img.show()
    img.save("static/out.jpg")

# Convert width height to a point in a rectangle
def getPoints(faceDictionary):
    shape = faceDictionary.face_rectangle
    left = shape.left
    top = shape.top
    right = left + shape.width
    bottom = top + shape.height
    
    return ((left, top), (right, bottom))
        
# Function to convert PIL image to URI        
def pil2datauri(img):
    data = BytesIO()
    img.save(data, "JPEG")
    data64 = base64.b64encode(data.getvalue())
    return u'data:img/jpeg;base64,'+data64.decode('utf-8')