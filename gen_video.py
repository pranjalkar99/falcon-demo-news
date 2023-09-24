import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, AudioFileClip

import gradio as gr

def create_video(img1, hl1, img2, hl2, img3, hl3, img4, hl4, img5, hl5):
    image_paths = []
    headlines = []
    
    if img1: image_paths.append(img1); headlines.append(hl1)
    if img2: image_paths.append(img2); headlines.append(hl2)
    if img3: image_paths.append(img3); headlines.append(hl3)
    if img4: image_paths.append(img4); headlines.append(hl4)
    if img5: image_paths.append(img5); headlines.append(hl5)

    # # List of image file paths and corresponding headlines
    # image_paths = ["download.jpeg", "download (1).jpeg",
    #                "download (2).jpeg", "download (3).jpeg"]
    # headlines = ["Foreign Minister S Jaishankar calls out Canada's apathy towards Khalistan terrorism",
    #              "India raises alarm over inaction by Canada on Khalistan terror during QUAD meet",
    #              "S Jaishankar puts Canada in the spotlight for being a 'terror haven'",
    #              "QUAD allies support India's concerns over Canada's handling of Khalistan terrorists"]

    # Calculate the common frame size
    max_width = max([cv2.imread(image_path).shape[1] for image_path in image_paths])
    max_height = max([cv2.imread(image_path).shape[0] for image_path in image_paths])
    frame_size = (max_width, max_height)

    # Output video settings
    output_file = "output_long.mp4"
    image_duration = 20
    frame_rate = 1 / image_duration

    def add_headline(image, headline, background_color=(0, 0, 0)):
        img_pil = Image.fromarray(image)
        draw = ImageDraw.Draw(img_pil)
        font = ImageFont.truetype("arial.ttf", 16)
        text_position = (10, image.shape[0] - 50)
        text_color = (255, 255, 255)

        max_text_width = image.shape[1] - text_position[0] * 2
        lines = []
        line = ""
        for word in headline.split():
            test_line = line + ("" if line == "" else " ") + word
            if draw.textsize(test_line, font=font)[0] <= max_text_width:
                line = test_line
            else:
                lines.append(line)
                line = word
        lines.append(line)

        total_text_height = sum(draw.textsize(line, font=font)[1] for line in lines)
        background_rect = [(text_position[0], text_position[1]), (image.shape[1] - text_position[0], text_position[1] + total_text_height)]
        draw.rectangle(background_rect, fill=background_color)

        y_position = text_position[1]
        for line in lines:
            text_width, text_height = draw.textsize(line, font=font)
            text_position = ((image.shape[1] - text_width) / 2, y_position)
            draw.text(text_position, line, fill=text_color, font=font)
            y_position += text_height

        return np.array(img_pil)

    # Create frames for the video
    frame_rate = 30  # Standard frame rate

    # Create frames for the video
    frames = []
    for image_path, headline in zip(image_paths, headlines):
        img = cv2.imread(image_path)
        img = cv2.resize(img, frame_size)
        img_with_headline = add_headline(img, headline)

        # Duplicate frames to match the desired duration
        for _ in range(int(frame_rate * image_duration)):
            frames.append(img_with_headline)

    # Save the frames as a video
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_file, fourcc, frame_rate, frame_size)

    for frame in frames:
        out.write(frame)

    out.release()
    cv2.destroyAllWindows()

    # Adding background music
    video = VideoFileClip(output_file)
    music = AudioFileClip("Epic-Chase(chosic.com).mp3")

    # Clip the music to match the video's duration
    music = music.subclip(0, video.duration)

    video_with_music = video.set_audio(music)
    video_with_music.write_videofile("output_with_music.mp4", codec="libx264", audio_codec="aac")
    return "output_with_music.mp4"
def hello_world(name):
    return f"Hello World, {name}!"

iface1 = gr.Interface(
    fn=hello_world,
    inputs=gr.inputs.Textbox(placeholder="Enter your name"),
    outputs="text"
)

# Define Gradio interface
iface2 = gr.Interface(
    fn=create_video,
    inputs=[
        gr.inputs.Image(type="filepath", label="Upload Image 1", optional=True),
        gr.inputs.Textbox(lines=2, placeholder="Enter Headline 1", optional=True),
        gr.inputs.Image(type="filepath", label="Upload Image 2", optional=True),
        gr.inputs.Textbox(lines=2, placeholder="Enter Headline 2", optional=True),
        gr.inputs.Image(type="filepath", label="Upload Image 3", optional=True),
        gr.inputs.Textbox(lines=2, placeholder="Enter Headline 3", optional=True),
        gr.inputs.Image(type="filepath", label="Upload Image 4", optional=True),
        gr.inputs.Textbox(lines=2, placeholder="Enter Headline 4", optional=True),
        gr.inputs.Image(type="filepath", label="Upload Image 5", optional=True),
        gr.inputs.Textbox(lines=2, placeholder="Enter Headline 5", optional=True),
    ],
    outputs=gr.outputs.Video(label="Generated Video"),
    title="Generate News AI",
    description="Add upto 5 images and headlines generated earlier...",
)

demo = gr.TabbedInterface([iface1, iface2], ["Get headlines", "Generate videos"])
demo.launch(debug=True,share=True)

