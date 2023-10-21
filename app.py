#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, io, yaml
from datetime import datetime
import uuid
from flask import Flask, render_template, request, make_response
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

import speech2text as s2t

app = Flask(__name__)

# Configuration
with open('config/settings.yml', 'r') as file:
    setting = yaml.safe_load(file)

account_name = setting["storage_account"]
account_url = f"https://{account_name}.blob.core.windows.net"
account_key = os.environ["STORAGE_KEY"] # In deployment make sure the variable exists
container_name = setting["storage_container"]

# Initialize Blob Service Client
blob_service_client = BlobServiceClient(account_url=account_url, credential=account_key)
container_client = blob_service_client.get_container_client(container_name)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file part"

        file = request.files["file"]
        if file.filename == "":
            return "No selected file"

        # Generate a uniquetim-stamped filename
        now = datetime.now()
        formatted_date = now.strftime("%Y%m%d%H%M%S")
        unique_filename = os.path.splitext(file.filename)[0] + formatted_date + os.path.splitext(file.filename)[1]  
        unique_filepath = os.path.join("data/mp3s",unique_filename)
        blob_client = container_client.get_blob_client(unique_filepath)

        if os.path.splitext(unique_filename)[1] == '.mp3':
            # Upload the file to Azure Blob Storage
            blob_client.upload_blob(file, content_type="audio/mpeg")

            # Run the speech2text pipeline
            try: 
                mp3_file = s2t.get_blob(unique_filepath)
            except:
                print("Error occurred in get_blob")
            try:
                wav_file = s2t.make_wav_from_mp3(mp3_file)
            except:
                print("Error occurred in make_wave_from_mp3")
            try:
                txt_file = s2t.make_transcript(wav_file)
            except:
                print("Error occurred in make_transcription")
            try:
                sum_file = s2t.make_summary(txt_file)
            except:
                print("Error occurred in make_summary")
            # Post the resulting files
            try:
                s2t.post_blobs()
            except:
                print("Error occurred in post_blobs")

        return "File uploaded successfully"

    return render_template("index.html")

@app.route('/summaries')
def list_blobs():
    subfolder_name = "data/summaries/"
    blobs = [blob.name[len(subfolder_name):] for blob in container_client.list_blobs(name_starts_with=subfolder_name)]
    return render_template('summaries.html', blobs=blobs)

@app.route('/download/<blob_name>')
def download(blob_name):
    subfolder_name = "data/summaries/"
    blob_client = container_client.get_blob_client(subfolder_name + blob_name)
    blob_data = blob_client.download_blob().readall()
    
    response = make_response(blob_data)
    response.headers['Content-Type'] = 'application/octet-stream'
    response.headers['Content-Disposition'] = f'attachment; filename={blob_name}'

    return response

# This route is still in development
@app.route('/downloads/<file_type>/<blob_name>')
def download(file_type, blob_name):
    subfolder_name = f"data/{file_type}/"
    blob_client = container_client.get_blob_client(subfolder_name + blob_name)
    blob_data = blob_client.download_blob().readall()
    
    response = make_response(blob_data)
    response.headers['Content-Type'] = 'application/octet-stream'
    response.headers['Content-Disposition'] = f'attachment; filename={blob_name}'

    return response

if __name__ == "__main__":
    app.run(debug=True)