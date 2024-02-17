import os
from convert_video import convert_video, generate_thumbnail

# test rig for video ingestion
# in parent directory, run with
# python utils/test.py
# produces output.mp4, frame.jpg, and frame.png

converted_video_file = "output.mp4"

convert_video(input_file="test_input.mp4",
              output_file=converted_video_file)

generate_thumbnail(input_file=converted_video_file,
                   output_file_base="frame")
