# NASA Astronomy Picture of the Day Wallpaper

A Python desktop application that retrieves NASA's Astronomy Picture of the Day (APOD), displays its accompanying explanation, and allows users to set the image as their Windows desktop wallpaper.

<img width="500" height="500" alt="APOD Logo" src="https://github.com/user-attachments/assets/eadcf6d0-5e21-446e-af2b-33d010013a81" />

## About the Project

NASA's Astronomy Picture of the Day showcases fascinating images of space, astronomy and scientific discoveries, accompanied by explanations written by professional astronomers.

As someone interested in astronomy and programming, I wanted to create a simple application that would allow me to discover these images while easily using them as desktop wallpapers.

The application retrieves the latest APOD content, displays it through a graphical user interface (GUI), and provides options to save, copy or apply the image as a wallpaper.

## Features

- **NASA APOD Integration:** Retrieves the latest astronomy image, title and explanation from NASA.
- **Wallpaper Customisation:** Set the original image as your desktop wallpaper or use a fitted version.
- **Automatic Image Resizing:** Resizes images to fit a 1920×1080 background while preserving their aspect ratio, adding black borders where necessary.
- **Graphical Interface:** Displays the image and its accompanying explanation in a simple Tkinter window.
- **Image Management:** Right-click an image to save it locally or copy it to the clipboard.
- **Multimedia Support:** Includes functionality for displaying animated GIFs and video content.
- **Source Access:** Open the original NASA APOD page directly from the application.
## GUI
Here is the GUI for the application:

<img width="507" height="689" alt="APOD_SCREENSHOT" src="https://github.com/user-attachments/assets/70d9e652-02ba-49fa-986e-2e6925b888a0" />

## Technologies Used

The application was developed using **Python**, alongside several libraries:

- **Requests:** Communicates with NASA's API and downloads images.
- **Tkinter:** Provides the desktop graphical interface.
- **Pillow (PIL):** Handles image processing, resizing and formatting.
- **OpenCV:** Provides functionality for displaying video content.
- **PyWin32 and ctypes:** Interact with Windows functionality to manage wallpapers and clipboard operations.
- **python-dotenv:** Loads configuration settings from environment variables.

## Installation

The application is designed for Windows.

1. Clone or download this repository.
2. Install Python and the required dependencies.
3. Create or configure a `.env` file in the project directory.
4. Specify the directory where downloaded wallpapers should be saved.
5. Run `NASA_Wallpaper.py`.

Example `.env` configuration:

```env
NASA_KEY=your_api_key
WALLPAPER_PATH=C:\Users\YourName\Pictures\NASA
```

The application uses NASA's APOD service to retrieve the latest available content.

## Development and Challenges

One of the main challenges involved handling images with different resolutions and aspect ratios. Astronomy images are often unusually sized, meaning they cannot always fit a standard desktop background without stretching or cropping.

To address this, I implemented image resizing using Pillow, preserving the original aspect ratio while centring the image against a black background.

Another challenge involved handling different media formats and adapting to changes in NASA's API. This required additional error handling, response validation and improvements to how the application processes downloaded content.

Throughout development, I strengthened my understanding of API integration, GUI development, image processing, external libraries and debugging.


## Acknowledgements

All astronomy content is provided by [NASA's Astronomy Picture of the Day](https://apod.nasa.gov/apod/astropix.html).

This project is available under the MIT License.
