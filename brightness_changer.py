import pystray
from PIL import Image
import time
import win32api
from monitorcontrol import get_monitors

def change_luminance():
    global index
    for monitor in get_monitors():
        with monitor:
            monitor.set_luminance(brightnesses[index])

    if index < len(brightnesses) - 1:
        index += 1
    else:
        index = 0





def change():
    try:
        change_luminance()
    except ValueError:
        if quit_on_error:
            icon.visible = False
            win32api.MessageBox(0,
                                "Display brightness changer has quit because your display is not compatible. Check "
                                "whether DDC/CI is enabled on your monitor",
                                "Display not compatible")
            icon.stop()
            while icon.visible:
                time.sleep(5)


def stop():
    icon.visible = False
    icon.stop()
    while icon.visible:
        time.sleep(5)


def load_image(path):
    try:
        return Image.open(path)
    except FileNotFoundError:
        win32api.MessageBox(0, "Assets not found. Press OK to download...", "Icons not found")
        import requests
        images = [
            "https://raw.githubusercontent.com/covertpluto3502/brightness-changer/main/brightness.ico",
            "https://raw.githubusercontent.com/covertpluto3502/brightness-changer/main/laptop.ico",
            "https://raw.githubusercontent.com/covertpluto3502/brightness-changer/main/monitor.ico"
        ]
        for img in images:
            r = requests.get(img)
            with open(img.split("/")[-1], "wb") as f:
                f.write(r.content)
        return Image.open(path)

# change this to False if you are sure that your monitor is definitely compatible with this script
quit_on_error = True

# change this to an icon.
# Default icons:
#  laptop.ico
#  monitor.ico
#  brightness.ico
image = load_image('laptop.ico')

icon = pystray.Icon(
    'icon',
    image,
    'Change monitor brightness',
    (pystray.MenuItem('Change', action=change, default=True, visible=False),
     pystray.MenuItem('Exit', action=stop)
     )
)


brightnesses = [50, 75, 100, 1, 25]
index = 1






def set_all(luminance):
    try:
        for monitor in get_monitors():
            with monitor:
                monitor.set_luminance(luminance)
    except ValueError:
        if quit_on_error:
            icon.visible = False
            win32api.MessageBox(0,
                                "Display brightness changer has quit because your display is not compatible. Check "
                                "whether DDC/CI is enabled on your monitor",
                                "Display not compatible")
            icon.stop()
            while icon.visible:
                time.sleep(5)


set_all(50)

icon.run()
