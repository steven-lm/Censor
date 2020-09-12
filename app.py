import os, base64
from flask import Flask, render_template, request, flash

import json
import requests
from IPython.display import HTML

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
from PIL import Image, ImageDraw
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person, SnapshotObjectType, OperationStatusType

# Set the FACE_SUBSCRIPTION_KEY environment variable with your key as the value.
# This key will serve all examples in this document.
KEY = os.environ['FACE_SUBSCRIPTION_KEY']

# Set the FACE_ENDPOINT environment variable with the endpoint from your Face service in Azure.
# This endpoint will be used in all examples in this quickstart.
ENDPOINT = os.environ['FACE_ENDPOINT']
face_credentials = CognitiveServicesCredentials(KEY)
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Display the image that was uploaded
        image = request.files["file"]
        uri = "data:image/jpg;base64," + base64.b64encode(image.read()).decode("utf-8")
        image.seek(0)

        # Use the Computer Vision API to extract text from the image
        extract_text_from_image(image, face_client)

    else:
        # Display a placeholder image
        uri = "/static/placeholder.png"

    return render_template("index.html", image_uri=uri)

#background process happening without any refreshing
@app.route('/blur_pic')
def blur_pic():
    #print ("Hello")
    #return ("nothing")
    
    if request.method == "POST":
        # Display the image that was uploaded
        image = request.files["file"]
        uri = "data:image/jpg;base64," + base64.b64encode(image.read()).decode("utf-8")
        image.seek(0)

        # Use the Computer Vision API to extract text from the image
        extract_text_from_image(image, face_client)

    else:
        # Display a placeholder image
        uri = "/static/placeholder.png"

    return render_template("index.html", image_uri=uri)

# Function that extracts text from images
def extract_text_from_image(image, client):
    detected_faces = client.face.detect_with_stream(image=image)
    if not detected_faces:
        raise Exception('No face detected from image {}')
    else:
        for face in detected_faces:
            print(face.face_id)
            
    response = request.files["file"]
    img = Image.open(response)
    
    print('Drawing rectangle around face... see popup for results.')
    draw = ImageDraw.Draw(img)
    for face in detected_faces:
        draw.ellipse(getPoints(face), outline='red')

    # Display the image in the users default image browser.
    img.show()

# Convert width height to a point in a rectangle
def getPoints(faceDictionary):
    shape = faceDictionary.face_rectangle
    left = shape.left
    top = shape.top
    right = left + shape.width
    bottom = top + shape.height
    
    return ((left, top), (right, bottom))