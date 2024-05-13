import os
from ffmpeg import FFmpeg
from IPython.display import Image, display, Video
from ipywidgets import widgets, Box, Layout
import numpy as np
import io
from PIL import Image as PILImage
import json


def unique_path(original_path):
    if not os.path.exists(original_path):
        return original_path
    else:
        i = 1
        path = ".".join(original_path.split(".")[:-1]) + "_1." + original_path.split(".")[-1]
        while os.path.exists(path):
            i += 1
            path = ".".join(original_path.split(".")[:-1]) + "_{}.".format(i) + original_path.split(".")[-1]
        return path


def extract_frame(video_path, timestamp, output_path):
    """
    Extracts a frame from a video at a given timestamp.

    :param video_path: Path to the input video file.
    :param timestamp: Timestamp in seconds where the frame should be extracted.
    :param output_path: Path to the output image file.
    """
    if os.path.exists(output_path):
        os.remove(output_path)
    FFmpeg().input(video_path, ss=timestamp).output(output_path, vframes=1).execute()


def extract_interval(video_path, interval, output_path):
    """
    Extracts an interval from a video.

    :param video_path: Path to the input video file.
    :param interval: Tuple of start and end times in seconds.
    :param output_path: Path to the output video file.
    """
    duration = interval[1] - interval[0]
    if os.path.exists(output_path):
        return
    FFmpeg().input(video_path, ss=interval[0], t=duration).output(output_path).execute()


def concatenate_videos(video_paths, output_path):
    """
    Concatenates a list of videos end to end using the concat demuxer.

    :param video_paths: A list of paths to the video files.
    :param output_path: Path to the output concatenated video file.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if os.path.exists(output_path):
        os.remove(output_path)
    with open("concat_list.txt", "w") as f:
        for video_path in video_paths:
            f.write(f"file '{video_path}'\n")
    os.system(f'ffmpeg -f concat -safe 0 -i concat_list.txt -c:v copy -c:a libmp3lame "{output_path}" -y 2> ffmpeg.log')
    os.remove("concat_list.txt")


def numpy_to_image(numpy_array):
    # Normalize and convert the image to uint8
    numpy_array = (numpy_array * 255 / np.max(numpy_array)).astype("uint8")
    # Convert to PIL Image
    pil_img = PILImage.fromarray(numpy_array)
    # Create a bytes buffer to save the image
    buffer = io.BytesIO()
    # Save the image as a PNG to the buffer
    pil_img.save(buffer, format="PNG")
    # Get the PNG image bytes
    image_bytes = buffer.getvalue()
    # Create an IPython Image object
    ipy_image = Image(data=image_bytes)
    return ipy_image


def display_speaker_identification_form(supercuts):
    # Create a submit button
    submit_button = widgets.Button(description="Submit", layout=Layout(width="auto"))

    # Create a dictionary to hold the text widgets for each
    with open("diarization_mappings.json", "r") as f:
        speaker_mapping = json.load(f)
    text_widgets = {}
    speaker_mapping = {}

    # Display each image with a text field
    for video_id, speaker_id, supercut_path in supercuts:
        # Display the video
        video = Video(supercut_path, embed=True)
        display(video)

        # Create a text input widget
        text_input = widgets.Text(
            value="", placeholder="Enter speaker's name", description="Name:", disabled=False, layout=Layout(width="auto")
        )
        display(text_input)

        # Store the text widget in the dictionary with the collage id as key
        text_widgets[supercut_path] = text_input
        if video_id not in speaker_mapping:
            speaker_mapping[video_id] = {}
        speaker_mapping[video_id][speaker_id] = text_input

    # Function to handle the submit action
    def on_submit(b):
        # On submit, populate the id_to_name_mapping
        for video_id, video_speaker_mapping in speaker_mapping.items():
            for speaker_id, text_widget in video_speaker_mapping.items():
                speaker_name = text_widget.value
                speaker_mapping[video_id][speaker_id] = speaker_name

        with open("diarization_mappings.json", "w") as f:
            json.dump(speaker_mapping, f)

    # Bind the submit button to the on_submit function
    submit_button.on_click(on_submit)

    # Display the submit button
    display(submit_button)
