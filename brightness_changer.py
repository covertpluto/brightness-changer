import pystray
from PIL import Image, ImageOps
import time
import win32api
from monitorcontrol import get_monitors
from winreg import HKEY_CURRENT_USER as hkey, QueryValueEx as getSubkeyValue, OpenKey as getKey


def theme():
    value_meaning = {0: "Dark", 1: "Light"}
    try:
        key = getKey(hkey, "Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize")
        sub = getSubkeyValue(key, "AppsUseLightTheme")[0]
    except FileNotFoundError:
        # some headless Windows instances (e.g. GitHub Actions or Docker images) do not have this key
        return None
    return value_meaning[sub]


def isLight():
    if theme() is not None:
        return theme() == 'Light'


def set_all(luminance):
    try:
        for monitor in get_monitors():
            with monitor:
                monitor.set_luminance(luminance)
    except ValueError:
        pass


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


# since PIL could not invert the image, we need to do it manually
def invert_transparent(img):
    w, a = img.split()
    rgb_image = Image.merge("RGB", (w, w, w))
    inverted_image = ImageOps.invert(rgb_image)
    r2, g2, b2 = inverted_image.split()
    transparent_image = Image.merge("RGBA", (r2, g2, b2, a))
    return transparent_image


def load_image(path):
    try:
        img = Image.open(path)
        if isLight():
            # invert the image if the user is using light mode
            img = invert_transparent(img)
            return img
        else:
            # if the user is using dark mode, return the image as is
            return img
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
        # try doing it again having found the icons
        return load_image(path)


# change this to False if you are sure that your monitor is definitely compatible with this script
quit_on_error = True

# change this to an icon.
# Default icons:
#  laptop.ico
#  monitor.ico
#  brightness.ico
image = load_image('brightness.ico')

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





set_all(50)

icon.run()
