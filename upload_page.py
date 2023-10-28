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
        return_notice = st.warning(f"File with name {uploaded_file.name} already exists in {destination_folder} on {container_name}")
    else:
        blob_client.upload_blob(uploaded_file.getbuffer())
        return_notice = st.success(f"Uplooaded file {uploaded_file.name} to {destination_folder} on {container_name}")
    return return_notice

def blob_download_button(button_message, blob_path):
    blob_client = container_client.get_blob_client(blob_path)
    blob_data = blob_client.download_blob().readall()
    data_type = 'application/octet-stream'
    file_name = os.path.basename(blob_path)
    
    return st.download_button(button_message, blob_data, file_name)

def blob_exists(mp3_name,extension):
    """
    Check if blob already exists, to avoid unnecessary processing
    Input: base name of the mp3, file extension
    Output: Boolean
    """
    mp3_name_stem = os.path.splitext(os.path.basename(mp3_name))[0]
    blob_path = os.path.join(setting[extension+"_folder"],mp3_name_stem+"."+extension)
    blob_client = container_client.get_blob_client(blob_path)
    return blob_client.exists()

def run_s2t_pipeline(mp3_blob):
    """
    Run the speech2text pipeline, create wav, txt and summary files from mp3
    Upload the resulting files to blob.
    Input: blob of the mp3
    Output: success message
    """
    # Get the blob available locally
    mp3_file = s2t.get_blob(mp3_blob)
    # Run pipeline where output file does not yet exist
    if not blob_exists(mp3_file,"wav"):
        wav_file = s2t.make_wav_from_mp3(mp3_file)
    if not blob_exists(mp3_file,"txt"):
        txt_file = s2t.make_transcript(wav_file)
    if not blob_exists(mp3_file,"sum"):
        sum_file = s2t.make_summary(txt_file)
    # Post the resulting files
    s2t.post_blobs()
    return st.success("s2t pipeline has run")

def run_mp4_pipeline(mp3_blob, png_blob):
    """
    Run the mp4 pipeline, create mp4 from mp3 and png
    Upload the resulting mp4 file to b"lob.
    Input: blob of the mp3 and blob of the png
    Output: success message
    """
    mp3_file = s2t.get_blob(mp3_blob)
    png_file = s2t.get_blob(png_blob)
    if not blob_exists(mp3_file,"mp4"):
        mp4_file = s2t.make_mp4(mp3_file,png_file)
    # Post the resulting files
    s2t.post_blobs()
    return st.success("mp4 pipeline has run")

# App set-up

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
        save_uploaded_file(setting["mp3_folder"], uploaded_mp3)
        mp3_path = os.path.join(setting["mp3_folder"], uploaded_mp3.name)
        transcript_request = st.button("Create summary")
        if transcript_request:
            with st.spinner("Working on transcript and summary"):
                run_s2t_pipeline(mp3_path)
                st.success("Transcript and summary complete!")
            # Create download buttons
            summary_name = os.path.splitext(uploaded_mp3.name)[0] + ".summary"
            blob_download_button("Download summary", os.path.join(setting["sum_folder"],summary_name))

with col2:
    uploaded_png = st.file_uploader("Upload your .png file here", type=["png"])
    if uploaded_png is not None:
        save_uploaded_file("data/pngs",uploaded_png)
        png_path = os.path.join(setting["png_folder"], uploaded_png.name)
        if uploaded_mp3 is not None:
            mp4_request = st.button("Create mp4")
            if mp4_request:
                with st.spinner("Working on mp4"):
                    mp4_path = os.path.join(setting["mp4_folder"],os.path.splitext(uploaded_mp3.name)[0]+".mp4")
                    blob_client = container_client.get_blob_client(mp4_path)
                    if blob_client.exists():
                        run_mp4_pipeline(mp3_path, png_path)
                        st.success("mp4 complete!")
                    else:
                        st.warning("mp4 already exists")
                mp4_name = os.path.splitext(uploaded_mp3.name)[0] + ".mp4"
                blob_download_button("Download mp4", os.path.join(setting["mp4_folder"],mp4_name))
