#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, yaml
import time
from datetime import datetime

# Configuration
with open('config/settings.yml', 'r') as file:
    setting = yaml.safe_load(file)

def get_file(input_file):
    """
    Create copy of source file in folder 'processing'
    Input: path of the source file
    Output: the path of the destination file 
    """
    destination_file = os.path.join(setting["proc_folder"], os.path.basename(input_file))
    
    cmd = f'cp "{input_file}" "{destination_file}"'
    os.system(cmd)

    return destination_file

def get_blob(blob_name):
    """
    Create copy of source blob (in fixed storage account and container) in folder 'processing'
    Input: path of the source blob
    Output: the path of the destination file
    """

    from azure.storage.blob import BlobServiceClient

    account_name = setting["storage_account"]
    account_url = f"https://{account_name}.blob.core.windows.net"
    account_key = os.environ["STORAGE_KEY"] # In deployment make sure the variable exists
    container_name = setting["storage_container"]

    # Create client objects
    blob_service_client = BlobServiceClient(account_url=account_url, credential=account_key)
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)

    # Download the blob
    destination_file = os.path.join(setting["proc_folder"],os.path.basename(blob_name))
    
    with open(destination_file, "wb") as f:
        blob_data = blob_client.download_blob()
        blob_data.readinto(f)

    return destination_file

def make_wav_from_mp3(mp3_file):
    """
    Converts an mp3 file into a wav file to facilitate text to speech 
    Input: local mp3 filename
    Output: local wav filename
    """
    from pydub import AudioSegment

    base_name = os.path.splitext(mp3_file)[0]
    wav_file = base_name + ".wav"
    sound = AudioSegment.from_file(mp3_file,format="mp3")

    sound.export(wav_file, format="wav")
    # soud_duration_seconds = len(sound) / 1000

    return wav_file

def make_transcript(wav_file):
    """
    Uses Azure cognitive Services to make transcript of wav file
    Input: path to wav file
    Output: path to txt file with transcript
    """    
    import azure.cognitiveservices.speech as speechsdk
    
    # Set the configuration for speech recognition 
    speech_config = speechsdk.SpeechConfig(
        subscription = os.environ["SPEECH_KEY"], 
        region = os.environ["SPEECH_REGION"])
    speech_config.speech_recognition_language="en-GB"
    speech_config.output_format = speechsdk.OutputFormat.Detailed
    # now = datetime.now()
    # formatted_date = now.strftime("%Y%m%d%H%M%S")
    speech_config.set_property(speechsdk.PropertyId.Speech_LogFilename, "data/speechsdk.log")

    audio_config = speechsdk.audio.AudioConfig(filename=wav_file)

    # Create a speech recognizer using the speech config and audio input config
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    # Define event handlers for recognizing speech and detecting when speech has stopped

    transcript = []

    base_name = os.path.splitext(wav_file)[0]
    transcript_file = base_name + ".txt"

    # Define event handlers for recognizing speech and detecting when speech has stopped
    def on_recognized(evt):
        """
        Callback that writes recognized speech to file
        """
        result = evt.result
        nonlocal transcript
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            transcript.append(result.text)
        elif result.reason == speechsdk.ResultReason.NoMatch:
            transcript.append(" --- No speech could be recognized. --- ")

    transcript_complete = False
    
    def on_session_end(evt):
        """
        callback that signals to stop continuous recognition upon receiving an event `evt
        """
        print(f"Session stopped on {evt}")
        # Stop recognition and close properly
        speech_recognizer.stop_continuous_recognition()
        nonlocal transcript_complete
        transcript_complete = True
        
    # Add printed output to track what happens
    speech_recognizer.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt)))
    speech_recognizer.recognized.connect(lambda evt: print('RECOGNIZED: {}'.format(evt)))
    speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
    speech_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
    speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))

    # Wire up the event handlers
    speech_recognizer.recognized.connect(on_recognized)
    speech_recognizer.session_stopped.connect(on_session_end)
    speech_recognizer.canceled.connect(on_session_end)
    
    speech_recognizer.start_continuous_recognition()

    while not transcript_complete:
        time.sleep(0.5)
    
    print(transcript)

    for phrase in transcript:
        with open(transcript_file,"a") as f:
            f.write(phrase + "\r\n")

    return transcript_file

def make_summary(transcript_file):
    """
    Use ChatGPT to create a summary of the transcript file
    Input: Path to the transcript file
    Output: Path to the summary file
    """
    import openai
    import tiktoken

    openai.organization = os.environ["OPENAI_ORG"]
    openai.api_key = os.environ["OPENAI_API_KEY"]
    
    openai_model = "gpt-3.5-turbo"
    instruction = "You write from the perspective of coach Kramer (she/her). You summarize for a busy executive."

    # Get the transcription from file
    with open(transcript_file,"r") as f:
        transcript = f.read()

    encoding = tiktoken.encoding_for_model(openai_model)
    transcript_length = len(encoding.encode(transcript))

    if transcript_length > 4000:
        response = "--- Transcript too long for ChatGPT ---"
    else:
        # Generate a summary using the OpenAI API
        response = openai.ChatCompletion.create(
            model = openai_model,
            messages=[
                {"role": "system", "content": instruction},
                {"role": "user", "content": transcript}
            ],
            max_tokens=150  # Adjust the value as needed to control the length of the summary
        )

    # Write the summary to a file with extension .summary
    base_name = os.path.splitext(transcript_file)[0]
    summary_file = base_name+".sum"

    with open(summary_file, "a") as f:
        f.write(response.choices[0].message['content'])
        f.write("\r\n")

    print(response)

    return summary_file, response

def make_mp4(mp3_file, png_file):
    """
    Use ffmpeg to add static image to mp3 and save as mp4
    Input: Path to the mp3 file and path to png file
    Output: Path to the mp4 file
    """
    mp4_file = os.path.splitext(mp3_file)[0]+".mp4"
    cmd = f"ffmpeg -loop 1 -framerate 1 -i \"{png_file}\" -i \"{mp3_file}\" -map 0:v -map 1:a -r 10 -vf \"scale='iw-mod(iw,2)':'ih-mod(ih,2)',format=yuv420p\" -movflags +faststart -shortest -fflags +shortest -max_interleave_delta 100M \"{mp4_file}\""
    os.system(cmd)
    return mp4_file

def post_files():
    """
    Run through files in "processing" folder
    Use file extension to send file to correct destination (local folder)
    Input: None
    Output: List of posted file destinations
    """
    posted_files = []

    for file_name in os.listdir(setting["proc_folder"]):
        # Determine destinationbased on file extension
        extension = os.path.splitext(file_name)[1]
        match extension:
            case ".wav":
                dst_folder = setting["wav_folder"]
            case  ".txt":
                dst_folder = setting["txt_folder"]
            case ".sum":
                dst_folder = setting["sum_folder"]
            case ".mp4":
                dst_folder = setting["mp4_folder"]
            case _:
                dst_folder = "."

        # Move file to destination - or delete
        if dst_folder != ".":
            posted_files.append(dst_folder + file_name)
            cmd = f'mv "{os.path.join(setting["proc_folder"],file_name)}" "{posted_files[-1]}"'
            os.system(cmd)
        else:
            cmd = f'rm "{os.path.join(setting["proc_folder"],file_name)}"'
            os.system(cmd)


    return post_files

def post_blobs():
    """
    Run through files in "processing" folder
    Use file extension to send file to correct destination (blob)
    Input: None
    Output: List of posted file destinations
    """

    from azure.storage.blob import BlobServiceClient

    posted_files = []

    account_name = setting["storage_account"]
    account_url = f"https://{account_name}.blob.core.windows.net"
    account_key = os.environ["STORAGE_KEY"] # In deployment make sure the variable exists
    container_name = setting["storage_container"]

    # Create client objects
    blob_service_client = BlobServiceClient(account_url=account_url, credential=account_key)

    for file_name in os.listdir(setting["proc_folder"]):
        # Determine destinationbased on file extension
        extension = os.path.splitext(file_name)[1]
        match extension:
            case ".wav":
                dst_folder = setting["wav_folder"]
            case  ".txt":
                dst_folder = setting["txt_folder"]
            case ".sum":
                dst_folder = setting["sum_folder"]
            case ".mp4":
                dst_folder = setting["mp4_folder"]
            case _:
                dst_folder = "."
         # Move file to destination - or delete
        if dst_folder != ".":
            target_blob = os.path.join(dst_folder,file_name)
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=target_blob)    
            try: 
                with open(file=os.path.join(setting["proc_folder"],file_name), mode="rb") as f:
                    blob_client.upload_blob(f, overwrite=True)
                posted_files.append(os.path.join(dst_folder,file_name))
                cmd = f'rm \"{os.path.join(setting["proc_folder"],file_name)}\"'
            except:
                cmd = f"echo Failed to upload {file_name}"
            os.system(cmd)       
        else:
            cmd = f'rm "{os.path.join(setting["proc_folder"],file_name)}"'
            os.system(cmd)

if __name__== "__main__":
    #Specify  source file
    source_file = "data/mp3s/actors.mp3"

    # # Set environment variables
    # from dotenv import load_dotenv

    # env_file = "secrets/.env"
    # load_env_result = load_dotenv(env_file, override=True)
    # Get the input file
    mp3_file = get_blob(source_file)
    # Run the pipeline
    wav_file = make_wav_from_mp3(mp3_file)
    txt_file = make_transcript(wav_file)
    sum_file = make_summary(txt_file)
    # Post the resulting files
    post_blobs()
