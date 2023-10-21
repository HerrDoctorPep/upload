import os, io, yaml
from datetime import datetime
import uuid
import time
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

import streamlit as st

# Configuration

st.write(os.getcwd())

with open(os.path.join(os.getcwd(),"config/settings.yml"), 'r') as file:
    setting = yaml.safe_load(file)

account_name = setting["storage_account"]
account_url = f"https://{account_name}.blob.core.windows.net"
account_key = os.environ["STORAGE_KEY"] # In deployment make sure the variable exists
container_name = setting["storage_container"]

# Initialize Blob Service Client
blob_service_client = BlobServiceClient(account_url=account_url, credential=account_key)
container_client = blob_service_client.get_container_client(container_name)

def save_uploaded_file(destination_folder, uploaded_file):
    file_path = os.path.join(destination_folder,uploaded_file.name) 
    blob_client = container_client.get_blob_client(file_path)
    blob_client.upload_blob(uploaded_file.getbuffer(), content_type="audio/mpeg")
    
    return st.success(f"Uplooaded file {uploaded_file.name} to {destination_folder} on {container_name}")

st.markdown(
    """
    # Smart Mind Workbench
    Please add the podcast `.mp3` and the cover art `.png` below.
    Once these are added, action buttons for creating transcript and `.mp4` will appear.
    """
    )
col1, col2 = st.columns(2)

with col1:
    uploaded_mp3 = st.file_uploader("Upload your .mp3 file here", type=["mp3"])
    if uploaded_mp3 is not None:
        save_uploaded_file("data/mp3s", uploaded_mp3)
        transcript_request = st.button("Create transcript")
        if transcript_request:
            with st.spinner("Working on transcript"):
                time.sleep(2) # code will be added
                st.success("Transcript complete!")
with col2:
    uploaded_png = st.file_uploader("Upload your .png file here", type=["png"])
    if uploaded_png is not None:
        save_uploaded_file("data/pngs",uploaded_png)
        if uploaded_mp3 is not None:
            mp4_request = st.button("Create mp4")
            if mp4_request:
                with st.spinner("Working on mp4"):
                    time.sleep(2) # code will be added
                    st.success("mp4 complete!")
