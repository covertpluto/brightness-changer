import pystray
from PIL import Image
import time
import win32api
from monitorcontrol import get_monitors
from winreg import HKEY_CURRENT_USER as hkey, QueryValueEx as getSubkeyValue, OpenKey as getKey


def theme():
    """ Uses the Windows Registry to detect if the user is using Dark Mode """
    # Registry will return 0 if Windows is in Dark Mode and 1 if Windows is in Light Mode. This dictionary converts that output into the text that the program is expecting.
    valueMeaning = {0: "Dark", 1: "Light"}
    # In HKEY_CURRENT_USER, get the Personalisation Key.
    try:
        key = getKey(hkey, "Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize")
        # In the Personalisation Key, get the AppsUseLightTheme subkey. This returns a tuple.
        # The first item in the tuple is the result we want (0 or 1 indicating Dark Mode or Light Mode); the other value is the type of subkey e.g. DWORD, QWORD, String, etc.
        subkey = getSubkeyValue(key, "AppsUseLightTheme")[0]
    except FileNotFoundError:
        # some headless Windows instances (e.g. GitHub Actions or Docker images) do not have this key
        return None
    return valueMeaning[subkey]

def isDark():
    if theme() is not None:
        return theme() == 'Dark'

def isLight():
    if theme() is not None:
        return theme() == 'Light'

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
