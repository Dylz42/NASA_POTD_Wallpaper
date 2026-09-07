import os
import requests
import ctypes
from dotenv import load_dotenv

APOD_API = "https://api.nasa.gov/planetary/apod"

def main():
    """ Main Function """
    get_wallpaper()
   


def get_wallpaper():
    """ Get the wallpaper of the day and download it into this file to replace the old one"""
    load_dotenv()
    nasa_key = os.getenv('NASA_KEY')
    wallpaper_path = os.getenv('WALLPAPER_PATH')

    params = {
        "api_key": nasa_key,
        "thumbs": True
    }

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
    
    os.makedirs(os.path.dirname(wallpaper_path), exist_ok = True)

    with open(wallpaper_path,"wb") as file:
        file.write(apod_image_response.content)
    
    print("Download success")
    return True
    

main()