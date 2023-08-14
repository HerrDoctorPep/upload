#!/usr/bin/env python

import os
import uuid
from flask import Flask, render_template, request
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

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
        unique_filename = str(uuid.uuid4()) + "-" + file.filename
        blob_client = container_client.get_blob_client(unique_filename)

        # Upload the file to Azure Blob Storage
        blob_client.upload_blob(file)

        # Save to local file
        folder_name = os.path.dirname(__file__)
        file.save(os.path.join(folder_name,"data/mp3s",unique_filename))

        return "File uploaded successfully"

    return render_template("index.html")

if __name__ == "__main__":
    app.run()