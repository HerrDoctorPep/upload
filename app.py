#!/usr/bin/env python

import os
from datetime import datetime
import uuid
from flask import Flask, render_template, request
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

import speech2text as s2t

app = Flask(__name__)

# Configuration
account_name = "s2torage"
account_key = os.environ["STORAGE_KEY"] # In deployment make sure the variable exists
container_name = "s2t"

# Initialize Blob Service Client
blob_service_client = BlobServiceClient(account_url=f"https://{account_name}.blob.core.windows.net", credential=account_key)
container_client = blob_service_client.get_container_client(container_name)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file part"

        file = request.files["file"]
        if file.filename == "":
            return "No selected file"

        # Generate a unique filename
        # unique_filename = str(uuid.uuid4()) + "-" + file.filename
        now = datetime.now()
        formatted_date = now.strftime("%Y%m%d%H%M%S")
        unique_filename = os.path.splitext(file.filename)[0] + formatted_date + os.path.splitext(file.filename)[1]  
        unique_filepath = os.path.join("data/mp3s",unique_filename)
        blob_client = container_client.get_blob_client(unique_filepath)

        if os.path.splitext(unique_filename)[1] == '.mp3':
            # Upload the file to Azure Blob Storage
            blob_client.upload_blob(file, content_type="audio/mpeg")

            # Run the speech2text pipeline
            mp3_file = s2t.get_blob(unique_filepath)
            wav_file = s2t.make_wav_from_mp3(mp3_file)
            txt_file = s2t.make_transcript(wav_file)
            sum_file = s2t.make_summary(txt_file)
            # Post the resulting files
            s2t.post_blobs()

        return "File uploaded successfully"

    return render_template("index.html")

if __name__ == "__main__":
    app.run()