import os
import requests
import ctypes
from PIL import Image
from dotenv import load_dotenv


APOD_API = "https://api.nasa.gov/planetary/apod"

def main():
    """ Main Function """
    # Get the Wallpaper from the APOD API
    wallpaper_path = get_wallpaper()

    # Fit it to the given screen
    get_fit_wallpaper(wallpaper_path, 1920,1080)

    # Set the wallpaper as the background for the computer
    set_wallpaper(wallpaper_path)
   


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
    response.raise_for_status()

    apod_data = response.json()

    if apod_data["media_type"] == "image":
        apod_url = apod_data.get("hdurl", apod_data["url"])
    
    else:
        print("No image found")
        return None

    apod_image_response = requests.get(apod_url, timeout = 30)
    apod_image_response.raise_for_status()
    
    # Download the image and set the filename
    os.makedirs(os.path.dirname(wallpaper_path), exist_ok = True)

    with open(wallpaper_path,"wb") as file:
        file.write(apod_image_response.content)
    
    print("Download success")
    return wallpaper_path

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
main()