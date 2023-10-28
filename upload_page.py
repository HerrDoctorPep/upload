import os, yaml, time
import speech2text as s2t
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

import streamlit as st

# Configuration

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
    if blob_client.exists():
        return_notice = st.warning(f"File with name {uploaded_file.name}already exists in {destination_folder} on {container_name}")
    else:
        blob_client.upload_blob(uploaded_file.getbuffer())
        return_notice = st.success(f"Uplooaded file {uploaded_file.name} to {destination_folder} on {container_name}")
    
    return return_notice

def run_s2t_pipeline(file_path):
    # Run the speech2text pipeline
    mp3_file = s2t.get_blob(file_path)
    wav_file = s2t.make_wav_from_mp3(mp3_file)
    txt_file = s2t.make_transcript(wav_file)
    while not os.path.exists(txt_file):
        time.sleep(1)
        print("Waiting for transcript...")
    sum_file = s2t.make_summary(txt_file)
    # Post the resulting files
    s2t.post_blobs()
    return st.success("s2t pipeline has run")

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
    mp3_folder = "data/mp3s"
    if uploaded_mp3 is not None:
        save_uploaded_file(mp3_folder, uploaded_mp3)
        transcript_request = st.button("Create transcript")
        if transcript_request:
            with st.spinner("Working on transcript"):
                run_s2t_pipeline(os.path.join(mp3_folder, uploaded_mp3.name))
                st.success("Transcript complete!")
with col2:
    uploaded_png = st.file_uploader("Upload your .png file here", type=["png"])
    if uploaded_png is not None:
        save_uploaded_file("data/pngs",uploaded_png)
        if uploaded_mp3 is not None:
            mp4_request = st.button("Create mp4")
            if mp4_request:
                with st.spinner("Working on mp4"):
                    st.success("mp4 complete!")
