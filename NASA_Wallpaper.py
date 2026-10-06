import os
import re
import io
import html
import requests
import ctypes
import cv2
import shutil
import webbrowser
import win32clipboard
from PIL import Image, ImageTk
from dotenv import load_dotenv
from urllib.parse import urlparse
import tkinter as tk
from tkinter import filedialog


APOD_API = "https://science.nasa.gov/wp-json/wp/v2/apod-basic/"

def main():
    """ Main Function """

    # Get the Wallpaper, Title and Description from the APOD API
    response = get_wallpaper()

    if response is not None:
        wallpaper_path, apod_title, apod_description, apod_media_url, media_type = response

    else:
        wallpaper_path = None
        apod_title = "No Astronomy Picture of the Day"
        apod_description = "Sorry but there doesnt seem to be a suitable Astronomy Picture of the Day at the moment"
        apod_media_url = None
        media_type = None

    # Set the fitted wallpaper path to None initially
    fit_wallpaper_path = None

    if wallpaper_path is not None:

        # Fit it to the given screen
        fit_wallpaper_path = get_fit_wallpaper(
            wallpaper_path,
            1920,
            1080
        )

    # Open a window that displays the flavour text of the image recieved
    display_window(
        apod_title,
        apod_description,
        wallpaper_path,
        fit_wallpaper_path,
        apod_media_url,
        media_type
    )


def get_wallpaper():
    """ Get the wallpaper of the day and download it into this file to replace the old one"""
    load_dotenv()
    nasa_key = os.getenv('NASA_KEY')
    wallpaper_directory = os.getenv('WALLPAPER_PATH')

    params = {
        "api_key": nasa_key,
    }

    # Call the APOD API

    try:
        response = requests.get(APOD_API, params=params, timeout = 8)
        response.raise_for_status()

    except requests.RequestException as error:
        print(f"Error contacting NASA APOD API: {error}")
        return None

    apod_data = response.json()

    if isinstance(apod_data, list):
        if not apod_data:
            print("NASA returned no APOD data.")
            return None

    apod_data = apod_data[0]

    media_type = apod_data.get("media_type")
    apod_title = apod_data.get("title", "Astronomy Picture of the Day")

    apod_description = clean_html(
        apod_data.get("explanation", "No description available.")
    )

    apod_page_url = (
        apod_data.get("permalink")
        or apod_data.get("url")
    )

    apod_image_url = apod_data.get("hdurl")

    if media_type == "image":

        if not apod_image_url:
            print("NASA did not provide an image URL.")
            return [
                None,
                apod_title,
                apod_description,
                apod_page_url,
                media_type
            ]

        try:
            apod_image_response = requests.get(
                apod_image_url,
                timeout=30
            )

            apod_image_response.raise_for_status()

            url_path = urlparse(apod_image_url).path

            extension = os.path.splitext(url_path)[1]

            if not extension:
                extension = ".jpg"

            wallpaper_path = os.path.join(
                wallpaper_directory,
                f"nasa_apod{extension}"
)

        except requests.RequestException as error:
            print(f"Could not download APOD image: {error}")

            return [
                None,
                apod_title,
                apod_description,
                apod_page_url,
                media_type
            ]

        if not wallpaper_path:
            print("WALLPAPER_PATH is not configured in .env")
            return None

        # Download the image
        directory = os.path.dirname(wallpaper_path)

        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(wallpaper_path, "wb") as file:
            file.write(apod_image_response.content)

        return [
            wallpaper_path,
            apod_title,
            apod_description,
            apod_page_url,
            media_type
        ]

    # Handle video and iframe data
    elif media_type in ("video", "iframe"):


        return [
            None,
            apod_title,
            apod_description,
            apod_page_url,
            media_type
        ]

    else:
        print(f"Unsupported APOD media type: {media_type}")

        return [
            None,
            apod_title,
            apod_description,
            apod_page_url,
            media_type
        ]


def clean_html(text):
    """Remove HTML tags from text returned by the new APOD API."""

    if not text:
        return ""

    # Convert things such as &amp; into &
    text = html.unescape(text)

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # Clean up excessive whitespace
    text = " ".join(text.split())

    # Remove the "Explanation:" prefix because we don't need it in the GUI
    if text.startswith("Explanation:"):
        text = text[len("Explanation:"):].strip()

    return text

def set_wallpaper(wallpaper_path):
    """Sets the image given at a path to be the wallpaper for the computer"""
    # Windows archaic variables necessary for setting the change
    wallpaper_action = 20
    update_user_profile = 0x01
    notify_change = 0x02

    try:
        ctypes.windll.user32.SystemParametersInfoW(wallpaper_action,0,wallpaper_path,update_user_profile | notify_change)
        print("Wallpaper Set")
        return True

    except Exception as e:
        print(f"Error changing wallpaper - {e}")
        return False

def get_fit_wallpaper(wallpaper_path, screen_width, screen_height):
    """ This function refits the image so that it is 1920 by 1080 for images of obscure resolutions"""
    # This function will overwrite the original file so a copy is necessary since the image will be opened
    with Image.open(wallpaper_path) as img:
        wallpaper = img.copy()

    # Use LANCZOS calculations to scale down the image to 1080p
    wallpaper.thumbnail((screen_width,screen_height), Image.Resampling.LANCZOS)

    # Create the background image and set it to all black
    background = Image.new(
        "RGB",
        (screen_width,screen_height),
        (0,0,0)
    )



    center_x = (screen_width - wallpaper.width)//2
    center_y = (screen_height - wallpaper.height)//2

    # Put the wallppaer on top of the black background
    background.paste(wallpaper, (center_x,center_y))

    directory = os.path.dirname(wallpaper_path)
    filename = os.path.basename(wallpaper_path)


    name, extension = os.path.splitext(filename)

    fitted_wallpaper_path = os.path.join(directory, f"{name}_fitted{extension}")

    # Save it separately instead of overwriting the original
    background.save(fitted_wallpaper_path)

    print(f"Wallpaper fitted: {fitted_wallpaper_path}")

    # Return the location of the new image
    return fitted_wallpaper_path

def display_window(apod_title, apod_description, apod_image_path, apod_fitted_image_path, apod_video_url, media_type):
    """ Creates a GUI with the Description for todays APOD """
    # Creates the root for the application
    display = tk.Tk()

    # Sets the title to be the title given by the APOD API
    display.title(f"APOD : {apod_title}")

    # Sets the size of the window
    display.geometry("500x650")
    display.resizable(False, False)
    
    # Resizes and adds the image to the application
    if media_type == "image":
        img = Image.open(apod_image_path)
        image_panel = tk.Label(display)
        save_menu = tk.Menu(display, tearoff=0)
        save_menu.add_command(label = "Save Image As...", command=lambda: save_image(apod_image_path))
        save_menu.add_command(label = "Copy Image", command=lambda: copy_image(apod_image_path))
        image_panel.bind("<Button-3>", lambda event: save(event,save_menu))
        image_panel.pack(side="top", fill="both", expand=True)

        if getattr(img, "is_animated", False):
            img.close()
            play_gif(apod_image_path, image_panel)
        
        else:
            
            img.thumbnail((500,400), Image.Resampling.LANCZOS)
            image = ImageTk.PhotoImage(img)
            image_panel.config(image = image)
            image_panel.image = image
            #image_panel.pack(side = "top", fill = "both", expand = "yes")
    
    elif media_type == "video":
        video_panel = tk.Label(display)
        video_panel.pack(side = "top", fill = "both", expand = "yes")
        play_video(apod_video_url, video_panel)

    #adds the text description of the application
    background = display.cget("bg")
    label_text = tk.Text(display, wrap="word",borderwidth=0, highlightthickness=0, height=10, bg=background)
    label_text.insert("0.1", apod_description)
    label_text.config(state="disabled")
    label_text.pack(side = "top", fill = "both", expand = False)

    

    button_frame = tk.Frame(display)
    button_frame.pack(pady=10)

    background_button = tk.Button(button_frame, text="Set Background", command=lambda: set_wallpaper(apod_image_path))
    fitted_background_button = tk.Button(button_frame, text="Set Fitted Background", command=lambda: set_wallpaper(apod_fitted_image_path))

    background_button.pack(side="left")
    fitted_background_button.pack(side="left")

    link_button = tk.Button(button_frame, text="View Source", command=lambda: webbrowser.open(apod_video_url))
    link_button.pack(side="left", padx=5)
    print("GUI Made!")
    display.mainloop()

def play_video(video_url, video_panel):
    """Play a video on the window based on the given link"""
    video = cv2.VideoCapture(video_url) # pylint: disable=E1101

    def update_frame():
        """ Update the frame displayed to create the video"""
        success, frame = video.read()

        if success:
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # pylint: disable=E1101

            image = Image.fromarray(frame)
            image.thumbnail((600, 400), Image.Resampling.NEAREST)

            photo = ImageTk.PhotoImage(image)

            video_panel.config(image=photo)
            video_panel.image = photo

            # Show the video at specified fps
            video_panel.after(42, update_frame)
        else:
            video.release()

    update_frame()

def play_gif(gif_path, image_panel):
    """Play a video on the window based on the given link"""
    gif = Image.open(gif_path)

    def update_frame(frame_number):
        """ Update the frame displayed to create the video"""
        gif.seek(frame_number)

        frame = gif.copy()

        frame.thumbnail(
            (500, 400),
            Image.Resampling.LANCZOS
        )

        photo = ImageTk.PhotoImage(frame)

        image_panel.config(image=photo)
        image_panel.image = photo

        # Get the duration of this frame from the GIF
        duration = gif.info.get("duration", 100)

        # Move to the next frame
        next_frame = (frame_number + 1) % gif.n_frames

        image_panel.after(
            duration,
            update_frame,
            next_frame
        )

    update_frame(0)

def save(event, menu):
    """When used, create a menu to save the file"""
    menu.tk_popup(event.x_root, event.y_root)

def save_image(apod_image_path):
    """Get the save location and save the file there"""
    save_location = filedialog.asksaveasfilename(initialfile=os.path.basename(apod_image_path))
    if save_location:
        shutil.copy(apod_image_path,save_location)

def copy_image(apod_image_path):
    """Copy the image to the clipboard"""
    with Image.open(apod_image_path) as img:
        with io.BytesIO() as output:
            img.convert("RGB").save(output,"BMP")
            bit_data = output.getvalue()
            bit_data = bit_data[14:]
            #Now put it in the clipboard
            win32clipboard.OpenClipboard()
            try:
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32clipboard.CF_DIB,bit_data)

            finally:
                win32clipboard.CloseClipboard()
main()
