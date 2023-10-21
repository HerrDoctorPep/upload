#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

def mp3_list_from_folder(folder_name = "data/mp3s"):
    """
    Add all mp3 file in the 
    """
    mp3_list = []

    for file_name in os.listdir(folder_name):
        if os.path.isfile(os.path.join(folder_name, file_name)):
            if os.path.splitext(file_name)[1] ==".mp3":
                mp3_list.append(file_name)
    return mp3_list

def mp4s_file_mp3_list(mp3_list,
                       mp3_folder="data/mp3s",
                       png_folder="data/pngs",
                       mp4_folder="data/mp4s"):
    for mp3_file in mp3_list:
        png_file = os.path.splitext(mp3_file)[0]+".png"
        mp4_file = os.path.splitext(mp3_file)[0]+".mp4"
        
        mp3_path = os.path.join(mp3_folder, mp3_file)
        png_path = os.path.join(png_folder, png_file)
        mp4_path = os.path.join(mp4_folder, mp4_file)
        
        mp4_list = []

        if os.path.isfile(png_path):
            if not os.path.exists(mp4_path):
                cmd = f"ffmpeg -loop 1 -framerate 1 -i \"{png_path}\" -i \"{mp3_path}\" -map 0:v -map 1:a -r 10 -vf \"scale='iw-mod(iw,2)':'ih-mod(ih,2)',format=yuv420p\" -movflags +faststart -shortest -fflags +shortest -max_interleave_delta 100M \"{mp4_path}\""
                os.system(cmd)
                mp4_list.append(mp4_file)
                print(f"Created {mp4_file}")
            else:
                print(f"File {mp4_file} already exists")
        else:
            print(f"No file {png_file} found")

if __name__== "__main__":
    mp3_list = mp3_list_from_folder("data/mp3s")
    mp4_list = mp4s_file_mp3_list(mp3_list)
