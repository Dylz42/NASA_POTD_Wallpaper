import os
import requests
import ctypes
import cv2
from PIL import Image, ImageTk
from dotenv import load_dotenv
import tkinter as tk


APOD_API = "https://api.nasa.gov/planetary/apod"

def main():
    """ Main Function """
    # Get the Wallpaper, Title and Description from the APOD API
    response = get_wallpaper()

    if response is not None:
        wallpaper_path, apod_title, apod_description, apod_video_url, media_type = response


    else:
        wallpaper_path = None
        apod_title = "No Astronomy Picture of the Day"
        apod_description = "Sorry but there doesnt seem to be a suitable Astronomy Picture of the Day at the moment"
        apod_video_url = None
        media_type = None


    if wallpaper_path is not None:
    # Fit it to the given screen
        get_fit_wallpaper(wallpaper_path, 1920,1080)

    # Set the wallpaper as the background for the computer
        set_wallpaper(wallpaper_path)

    # Open a window that displays the flavour text of the image recieved
    display_window(apod_title, apod_description, wallpaper_path, apod_video_url, media_type)
   


def get_wallpaper():
    """ Get the wallpaper of the day and download it into this file to replace the old one"""
    load_dotenv()
    nasa_key = os.getenv('NASA_KEY')
    wallpaper_path = os.getenv('WALLPAPER_PATH')

    params = {
        "api_key": nasa_key,
        "thumbs": True
    }

    # Call the APOD API
    response = requests.get(APOD_API, params=params, timeout = 8)
    if response.status_code is not 200:
        return None

    apod_data = response.json()

    if apod_data["media_type"] == "image":
        apod_url = apod_data.get("hdurl") or apod_data.get("url")
        apod_title = apod_data["title"]
        apod_description = apod_data["explanation"]
        apod_video_url = None
        media_type = apod_data["media_type"]
        
    elif apod_data["media_type"] == "video":
        apod_url = None
        apod_title = apod_data["title"]
        apod_description = apod_data["explanation"]
        apod_video_url = apod_data["url"]
        media_type = apod_data["media_type"]

    
    
    else:
        print("No supported image format")
        return None
    
    
    if not apod_url:
        print("No usable image url was returned by NASA")
        output = [None, apod_title, apod_description, apod_video_url, media_type]

        return output

    

    apod_image_response = requests.get(apod_url, timeout = 30)


    apod_image_response.raise_for_status()
    
    # Download the image and set the filename
    os.makedirs(os.path.dirname(wallpaper_path), exist_ok = True)

    with open(wallpaper_path,"wb") as file:
        file.write(apod_image_response.content)
    

    print("Download success")
    output = [wallpaper_path, apod_title, apod_description, apod_video_url, media_type]

    return output

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

    background.save(wallpaper_path)
    print("Wallpaper fitted :)")

def display_window(apod_title, apod_description, apod_image_path, apod_video_url, media_type):
    """ Creates a GUI with the Description for todays APOD """
    # Creates the root for the application
    display = tk.Tk()

    # Sets the title to be the title given by the APOD API
    display.title(f"APOD : {apod_title}")

    # Sets the size of the window
    display.geometry("500x600")

    # Resizes and adds the image to the application
    if media_type == "image":
        img = Image.open(apod_image_path)

        img.thumbnail((500,400), Image.Resampling.LANCZOS)

        image = ImageTk.PhotoImage(img)
        image_panel = tk.Label(display, image = image)
        image_panel.pack(side = "top", fill = "both", expand = "yes")
    
    elif media_type == "video":
        video_panel = tk.Label(display)
        video_panel.pack(side = "top", fill = "both", expand = "yes")
        play_video(apod_video_url, video_panel)

    #adds the text description of the application
    label_text = tk.Label(display, text = apod_description, wraplength=450)
    label_text.pack(side = "top", fill = "both", expand = "yes")

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

main()