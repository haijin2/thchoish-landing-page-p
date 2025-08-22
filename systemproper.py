# Hi! Please use my comments as guide for integrating the algorithm into the freeware. 
# See comments suggesting where you may input essential blocks of the algorithm (e.g. code for encryption/decryption, SQLite integration).
# Please do not hesitate to reach out if you need help understanding the landing page interface.
# In the name of academic integrity, I disclose that AI (OpenAI, Copilot) assisted in creating few functions, while I developed approximately 60% of the code.

# This is the documentation I used to further understand DearPyGUI: https://dearpygui.readthedocs.io/en/latest/
# Other resources: https://www.youtube.com/watch?v=2RocXKPPx4o, https://www.youtube.com/watch?v=FkN013q1Vx4&list=PLeOtHc_su2eVsj4QylvXYcyQsGu1Bwgp9

import os 
import sys 
import time # In this program, the time module is used when the app automatically returns to the password menu page (no button) after informing the user about errors in their password in the splash screen.
# (Splash screens cite as the solution used to address use cases requiring users to be aware of what is happening in the application). 
import shutil # The shutil module is used in saving processed images (encrypted and decrypted images) by taking advantage of its 'copy' method to select the mentioned images. This is one of the modules suggested by AI which works.
import uuid # The uuid module is used to give the uploaded images different file names. This is usable when two files have the same name. This is helpful in saving the images in SQLite.
import subprocess # The subprocess module is used to open Windows Explorer to select images or save files.
import re # The re module is used for password scoring (weak, strong).
import hashlib # Since this is a prototype of the GUI only, the original hashing algorithm is not integrated in the app. I imported hashlib to only create the splash screen while the password is actually hashing.
from PIL import Image, UnidentifiedImageError, ExifTags # The classes inside the Pillow library allow us to load and save images in Python and get EXIF metadata tags.
import dearpygui.dearpygui as dpg # The dearpygui library helps us create the GUI of the system proper.

# The tkinter library (through the filedialog module) allows us to interact with the file dialog inside the application (so the file dialog will not open outside of the application.)
try:
    import tkinter as tk
    from tkinter import filedialog
except Exception:
    tk = None
    filedialog = None

# Global variables
VALID_EXTS = (".jpg", ".jpeg", ".heic") # This application only accepts JPG, JPEG, and HEIC. PNG does not typically contain EXIF metadata.
STATE = {
    "mode": None, # This stores the current mode of the app. Initially, it is none (as user does not select steps yet), but its choices include encrypt, decrypt, view, and batch.
    "password": "", # This stores the current password. This could be an important variable in linking the application with its database.
    "last_paths": [], # This stores file paths recently opened. This is used in the program to let each function know what file we are currently working.
    "imgs_in_folder": [], # This stores file paths of images in selected folders.
    "textures": {}, # In this code, 'textures' refer to images. Since the Pillow library converts images into numpy arrays (based on pixel data), the 'texture' of DearPyGUI assembles them back to an image ready for display.
    "display_map": {}, #!IMPORTANT! The display map stores all the versions of the image (preprocessed, with blocks, and processed) uploaded.
}

# A function that allows users to go straightly to the Desktop folder when they open the Window Explorer.
def _default_desktop_dir():
    home = os.path.expanduser("~")
    desk = os.path.join(home, "Desktop")
    return desk if os.path.isdir(desk) else home

# This function helps us to interact with the Windows file explorer, for both selecting images and folders.
def open_in_explorer_external(path):
    if not path:
        return
    path = os.path.abspath(path)
    try:
        if sys.platform.startswith("win"):
            # This if statement is used for selecting images.
            if os.path.isfile(path):
                try:
                    subprocess.run(["explorer", f"/select,{path}"], check=False)
                except Exception:
                    try:
                        subprocess.Popen(f'explorer /select,"{path}"', shell=True)
                    except Exception:
                        pass
            # This else statement is used for selecting folders.
            else:
                try:
                    os.startfile(path)
                except Exception:
                    try:
                        subprocess.run(["explorer", path], check=False)
                    except Exception:
                        pass
    except Exception:
        pass

# This function is a placeholder function that assesses the strength of the password to be hashed. In the use cases provided, when the password is not strong, it will not hash. 
# For testing's purposes, passwords with at least one lower capital letter, one small capital letter, and a number are considered as strong (so when tested, the team will not type long passwords).
def password_is_strong(pw: str) -> bool:
    score = 0
    if len(pw) >= 12:
        score += 1
    has_lower = any(c.islower() for c in pw)
    has_upper = any(c.isupper() for c in pw)
    has_digit = any(c.isdigit() for c in pw)
    has_sym = any(not c.isalnum() for c in pw)
    score += sum([has_lower, has_upper, has_digit, has_sym])
    return score >= 3

# Lines 88 to 110 shall replace lines 76 to 85 in the actual program as the code below cites NIST password policy standards.
# def password_is_strong(pw: str) -> bool:
#    if len(pw) < 12:
#        return False

#    has_lower = re.search(r"[a-z]", pw) is not None
#    has_upper = re.search(r"[A-Z]", pw) is not None
#    has_digit = re.search(r"[0-9]", pw) is not None
#    has_symbol = re.search(r"[^a-zA-Z0-9]", pw) is not None

#    if not (has_lower and has_upper and has_digit and has_symbol):
#        return False

#    weak_patterns = [
#        "password", "123456", "qwerty", "letmein",
#        "admin", "welcome", "iloveyou", "monkey", "almv"
#    ]
#    if any(w in pw.lower() for w in weak_patterns):
#        return False

#    if re.fullmatch(r"(.)\1{5,}", pw):  
#        return False

#    return True

# The function below animates the progress bar for splash screens (I asked AI to assist me for this function). 
def simulate_progress_and_render(progress_tag, steps=10, delay=0.05):
    for i in range(1, steps + 1):
        try:
            dpg.set_value(progress_tag, i / steps)
        except Exception:
            pass
        try:
            dpg.render_dearpygui_frame()
        except Exception:
            pass
        time.sleep(delay)

# This function creates the actual texture to be stored in the state (texture) (in the global variable).
def get_or_create_texture_for_path(path, max_w, max_h):
    if not path:
        return None, 0, 0
    path_str = str(path)
    # The key is the unique identifier for the images uploaded (This naming convention is suggested by AI).
    key = f"tex::{path_str}::{int(max_w)}x{int(max_h)}"
    # This code checks if the image is already cached in the global state.
    if key in STATE["textures"]:
        tag, w, h = STATE["textures"][key]
        try:
            if dpg.does_item_exist(tag):
                return tag, w, h
        except Exception:
            pass

    # This is a great catch AI suggested when I asked it to correct the code. This is just to prevent early stopping when file does not exist.
    if not os.path.exists(path_str):
        return None, 0, 0

    # The following try-catch method is what actually converts the image into a texture.
    try:
        with Image.open(path_str) as img:
            img = img.convert("RGBA")

            # This tuple assigning gets the dimension of the preprocessed image.
            ow, oh = img.size
            if ow == 0 or oh == 0:
                return None, 0, 0
            
            # This line is another contribution of AI which helps the program to scale the images properly.
            scale = min(max_w / ow, max_h / oh)
            if scale >= 1.0:
                new_w, new_h = ow, oh
                scaled = img.copy()
            else:
                new_w = max(1, int(round(ow * scale)))
                new_h = max(1, int(round(oh * scale)))
                scaled = img.resize((new_w, new_h), Image.LANCZOS)

            # The following block of code converts the image into a byte array (as this is how DearPyGui processes images).
            raw = scaled.tobytes()
            arr = [c / 255.0 for c in raw]

            # In the documentation of DearPyGui, it is mentioned that it expects for the images to have tags.
            # Note that tag is different from key. Key is used for caching (storing the file path as a global variable), while tag is used as a DearPyGui requirement (for photos).
            tag = f"tex_{uuid.uuid4().hex}"

            # The next try-catch block is what actually saves the byte array into the texture state (in the global variables).
            try:
                with dpg.texture_registry(show=False):
                    dpg.add_static_texture(new_w, new_h, arr, tag=tag)
                STATE["textures"][key] = (tag, new_w, new_h)
                return tag, new_w, new_h
            except Exception:
                try:
                    dpg.add_static_texture(new_w, new_h, arr, tag=tag)
                    STATE["textures"][key] = (tag, new_w, new_h)
                    return tag, new_w, new_h
                except Exception:
                    return None, 0, 0
                
    except Exception:
        return None, 0, 0

# !IMPORTANT! This is a mock function only. Since this program serves as the UI only, the actual code which displays the preprocessed image, image with Shannon Entropy blocks, and processed image is not present.
# Once other teammates have integrated the database to the program, this function needs to be modified.
def get_three_side_by_side_textures(path, container_width=860, spacing=18, max_height=220, cols=3):
    if not path or not os.path.exists(path):
        return [None, None, None], 0, 0
    total_spacing = (cols - 1) * spacing
    slot_w = max(1, int((container_width - total_spacing) / cols))
    tag, w, h = get_or_create_texture_for_path(path, slot_w, max_height)
    if not tag:
        return [None, None, None], slot_w, max_height
    return [tag, tag, tag], w, h

# This is a very important function which checks for two things: if the image is either a JPG or a HEIC and if the image has an EXIF metadata.
# This function is entirely generated by AI. But after checking, it works as expected. 
def check_image_valid_and_has_exif(path, extract_metadata: bool = False):
    def _rat_to_float(r):
        try:
            if isinstance(r, (tuple, list)) and len(r) == 2:
                num, den = r
                if den == 0:
                    return float(num)
                return float(num) / float(den)
            if hasattr(r, "numerator") and hasattr(r, "denominator"):
                return float(r.numerator) / float(r.denominator)
            return float(r)
        except Exception:
            try:
                return float(str(r))
            except Exception:
                return None

    def _dms_to_decimal(dms, ref):
        try:
            if not dms or len(dms) < 3:
                return None
            deg = _rat_to_float(dms[0])
            minute = _rat_to_float(dms[1])
            sec = _rat_to_float(dms[2])
            if deg is None or minute is None or sec is None:
                return None
            dec = deg + (minute / 60.0) + (sec / 3600.0)
            if isinstance(ref, (bytes, bytearray)):
                ref = ref.decode("utf-8", errors="ignore")
            if isinstance(ref, str) and ref.upper() in ("S", "W"):
                dec = -abs(dec)
            return dec
        except Exception:
            return None
        
    _EXIF_TAGS = ExifTags.TAGS if hasattr(ExifTags, "TAGS") else {}
    _GPS_TAGS = ExifTags.GPSTAGS if hasattr(ExifTags, "GPSTAGS") else {}

    try:
        _, ext = os.path.splitext(str(path).lower())
    except Exception:
        return (False, False) if not extract_metadata else (False, False, {})

    if ext not in VALID_EXTS:
        return (False, False) if not extract_metadata else (False, False, {})

    try:
        with Image.open(path) as img:
            has_exif = False
            exif_dict = {}

            try:
                if hasattr(img, "getexif"):
                    raw = img.getexif()
                    if raw and len(raw.items()) > 0:
                        has_exif = True
                        for tag_id, val in raw.items():
                            name = _EXIF_TAGS.get(tag_id, tag_id)
                            exif_dict[name] = val
            except Exception:
                has_exif = False
                exif_dict = {}

            info = img.info or {}
            info_has_meta = any(
                k.lower() in ("exif", "comment", "text", "description", "author", "meta")
                for k in info.keys()
            )
            if isinstance(info, dict) and any(bool(v) for v in info.values()):
                info_has_meta = True

            has_meta = bool(has_exif or info_has_meta)

            if not extract_metadata:
                return True, has_meta

            meta = {
                "Date Taken": None,        # DateTimeOriginal
                "Program Name": None,      # Software
                "Date Acquired": None,     # DateTimeDigitized
                "Copyright": None,         # Copyright
                "Image ID": None,          # ImageUniqueID
                "Camera Maker": None,      # Make
                "Camera Model": None,      # Model
                "Lens Maker": None,        # LensMake
                "Lens Model": None,        # LensModel
                "EXIF Version": None,      # ExifVersion
                "Latitude": None,          # decimal degrees (float) or None
                "Latitude Ref": None,      # 'N'/'S' or None
                "Longitude": None,         # decimal degrees (float) or None
                "Longitude Ref": None,     # 'E'/'W' or None
                "Altitude": None,          # float or None
                "Altitude Ref": None       # altitude ref if present
            }

            meta["Date Taken"] = exif_dict.get("DateTimeOriginal") or exif_dict.get("DateTime")
            meta["Program Name"] = exif_dict.get("Software")
            meta["Date Acquired"] = exif_dict.get("DateTimeDigitized")
            meta["Copyright"] = exif_dict.get("Copyright")
            meta["Image ID"] = exif_dict.get("ImageUniqueID")

            meta["Camera Maker"] = exif_dict.get("Make")
            meta["Camera Model"] = exif_dict.get("Model")
            meta["Lens Maker"] = exif_dict.get("LensMake")
            meta["Lens Model"] = exif_dict.get("LensModel")
            meta["EXIF Version"] = exif_dict.get("ExifVersion")

            try:
                gps_raw = exif_dict.get("GPSInfo")
                if gps_raw:
                    gps_map = {}
                    if isinstance(gps_raw, dict):
                        any_numeric_key = any(isinstance(k, int) for k in gps_raw.keys())
                        if any_numeric_key:
                            for k, v in gps_raw.items():
                                name = _GPS_TAGS.get(k, k)
                                gps_map[name] = v
                        else:
                            gps_map = dict(gps_raw)
                    else:
                        gps_map = {}

                    lat = gps_map.get("GPSLatitude")
                    lat_ref = gps_map.get("GPSLatitudeRef")
                    lon = gps_map.get("GPSLongitude")
                    lon_ref = gps_map.get("GPSLongitudeRef")
                    alt = gps_map.get("GPSAltitude")
                    alt_ref = gps_map.get("GPSAltitudeRef")

                    lat_dec = _dms_to_decimal(lat, lat_ref) if lat is not None else None
                    lon_dec = _dms_to_decimal(lon, lon_ref) if lon is not None else None

                    alt_val = None
                    try:
                        if alt is not None:
                            alt_val = _rat_to_float(alt)
                    except Exception:
                        alt_val = None

                    meta["Latitude"] = lat_dec
                    meta["Latitude Ref"] = (lat_ref.decode() if isinstance(lat_ref, bytes) else lat_ref)
                    meta["Longitude"] = lon_dec
                    meta["Longitude Ref"] = (lon_ref.decode() if isinstance(lon_ref, bytes) else lon_ref)
                    meta["Altitude"] = alt_val
                    meta["Altitude Ref"] = (alt_ref.decode() if isinstance(alt_ref, bytes) else alt_ref)
            except Exception:
                pass

            return True, has_meta, meta

    except Exception:
        return (False, False) if not extract_metadata else (False, False, {})

# This function creates a a hidden Tkinter root window that is only used as a parent for file/folder dialogs (the function is fully generated by AI again).
# Without this code, the file dialog opens twice (inside and outside the application).
def _make_tk_root_for_dialog(initial_dir=None):
    if tk is None:
        return None
    root = tk.Tk()
    root.withdraw()
    try:
        root.attributes("-topmost", True)
    except Exception:
        pass
    try:
        root.update()
        root.lift()
        root.focus_force()
    except Exception:
        pass
    try:
        if initial_dir:
            os.chdir(initial_dir)
    except Exception:
        pass
    return root

# This function opens a native dialog but limit users in selecting JPG or HEIC files only.
def ask_open_file_jpg_heic():
    if tk is None or filedialog is None:
        return None
    initial_dir = _default_desktop_dir() if sys.platform.startswith("win") else ""
    root = _make_tk_root_for_dialog(initial_dir=initial_dir)
    try:
        path = filedialog.askopenfilename(parent=root, title="Select a JPG / HEIC image",
                                          initialdir=initial_dir,
                                          filetypes=[("JPEG / HEIC files", ("*.jpg", "*.jpeg", "*.heic")),
                                                     ("JPEG", ("*.jpg", "*.jpeg")), ("HEIC", "*.heic")])
    except Exception:
        path = filedialog.askopenfilename(parent=root, title="Select a JPG / HEIC image", filetypes=[("Image files", "*.jpg *.jpeg *.heic")])
    try:
        root.destroy()
    except Exception:
        pass
    return path or None

# This function opens a native dialog but limit users in selecting folders with JPG and HEIC files only.
def ask_select_directory():
    if tk is None or filedialog is None:
        return None
    initial_dir = _default_desktop_dir() if sys.platform.startswith("win") else ""
    root = _make_tk_root_for_dialog(initial_dir=initial_dir)
    try:
        folder = filedialog.askdirectory(parent=root, title="Select folder containing JPG / HEIC images", initialdir=initial_dir)
    except Exception:
        folder = filedialog.askdirectory(parent=root, title="Select folder containing JPG / HEIC images")
    try:
        root.destroy()
    except Exception:
        pass
    return folder or None

# This function saves all processed images as JPG files. The reason for this is JPG is universally supported. HEIC, while accepted by the program, might not be supported by other photo viewers.
def ask_save_file_jpg(default_name="image.jpg", initial_dir=None):
    """Open native Save As; initial_dir optional (defaults to Desktop on Windows)."""
    if tk is None or filedialog is None:
        return None
    if initial_dir is None:
        initial_dir = _default_desktop_dir() if sys.platform.startswith("win") else ""
    root = _make_tk_root_for_dialog(initial_dir=initial_dir)
    try:
        path = filedialog.asksaveasfilename(parent=root, title="Save image as", initialfile=default_name,
                                            defaultextension=".jpg", initialdir=initial_dir,
                                            filetypes=[("JPEG", ("*.jpg","*.jpeg")), ("All files", "*.*")])
    except Exception:
        path = filedialog.asksaveasfilename(parent=root, title="Save image as", initialfile=default_name, defaultextension=".jpg")
    try:
        root.destroy()
    except Exception:
        pass
    return path or None

# This function helps users to save the processed folder.
def ask_save_directory():
    if tk is None or filedialog is None:
        return None
    initial_dir = _default_desktop_dir() if sys.platform.startswith("win") else ""
    root = _make_tk_root_for_dialog(initial_dir=initial_dir)
    try:
        folder = filedialog.askdirectory(parent=root, title="Select folder to save images into", initialdir=initial_dir)
    except Exception:
        folder = filedialog.askdirectory(parent=root, title="Select folder to save images into")
    try:
        root.destroy()
    except Exception:
        pass
    return folder or None

# This is a fully AI-generated function which saves the images to a specific file destination.
def save_image_with_conversion(src_path, dest_path):
    try:
        dest_dir = os.path.dirname(dest_path)
        if dest_dir and not os.path.exists(dest_dir):
            os.makedirs(dest_dir, exist_ok=True)
    except Exception as e:
        return False, f"Failed to create destination directory: {e}"

    dest_ext = os.path.splitext(dest_path.lower())[1]
    try:
        if dest_ext in (".jpg", ".jpeg"):
            try:
                with Image.open(src_path) as im:
                    rgb = im.convert("RGB")
                    rgb.save(dest_path, format="JPEG", quality=95)
                return True, f"Saved (converted) to {dest_path}"
            except (UnidentifiedImageError, OSError):
                try:
                    shutil.copy2(src_path, dest_path)
                    return True, f"Saved by copy (fallback) to {dest_path}"
                except Exception as e2:
                    return False, f"Failed to save image: {e2}"
        else:
            try:
                shutil.copy2(src_path, dest_path)
                return True, f"Saved to {dest_path}"
            except Exception as e:
                return False, f"Failed to copy file: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"

# IMPORTANT NOTEEE ------------------------------------------------------------------------------------------------------------------------------------------------------------
# I will stop adding comments here for the time being, as providing extensive documentation for the code would take too much time and it is better to share this code as early as possible.
# I will try to continue the documentation on weekends and will update the GitHub repository as necessary.

# This function serves as the handler for selecting a single image.
def on_select_single(sender, app_data):
    path = ask_open_file_jpg_heic()
    if not path:
        show_page("action_success")
        return

    abspath = os.path.abspath(path)
    show_page("loading_validate")
    is_valid, has_meta = check_image_valid_and_has_exif(abspath)
    time.sleep(0.12)
    if not is_valid:
        dpg.set_value("loading_message", "Invalid format — we accept only JPG / HEIC.")
        show_page("loading_delay_then_back")
        simulate_progress_and_render("hash_progress", steps=1, delay=0.25)
        time.sleep(1.2)
        show_page("password")
        return

    show_page("loading_processing")
    simulate_progress_and_render("proc_progress", steps=10, delay=0.04)
    STATE["last_paths"] = [abspath]
    show_results(paths=STATE["last_paths"])

# This function serves as the handler for selecting a folder.
def on_select_folder(sender, app_data):
    folder = ask_select_directory()
    if not folder:
        show_page("action_success")
        return
    imgs = [os.path.abspath(os.path.join(folder, f)) for f in os.listdir(folder) if f.lower().endswith(VALID_EXTS)]
    if not imgs:
        dpg.set_value("loading_message", "No JPG / HEIC images found in selected folder.")
        show_page("loading_delay_then_back")
        simulate_progress_and_render("hash_progress", steps=1, delay=0.25)
        time.sleep(1.2)
        show_page("password")
        return
    if STATE["mode"] == "decrypt":
        STATE["imgs_in_folder"] = imgs
        build_image_selection_grid(imgs)
        show_page("image_selection")
        return

    show_page("loading_processing")
    simulate_progress_and_render("proc_progress", steps=12, delay=0.035)
    STATE["last_paths"] = imgs
    show_results(paths=STATE["last_paths"])


def build_image_selection_grid(imgs):
    if dpg.does_item_exist("selection_container"):
        children = dpg.get_item_children("selection_container", 1) or []
        for c in children:
            try:
                dpg.delete_item(c)
            except Exception:
                pass

    with dpg.group(parent="selection_container", horizontal=False):
        for p in imgs:
            with dpg.child_window(width=200, height=200):
                try:
                    tex, w, h = get_or_create_texture_for_path(p, 160, 120)
                    if tex:
                        dpg.add_image(tex, width=w, height=h)
                    else:
                        dpg.add_text(os.path.basename(p))
                except Exception:
                    dpg.add_text(os.path.basename(p))
                safe_tag = f"chk_{hashlib.sha1(str(p).encode()).hexdigest()}"
                dpg.add_checkbox(label="Include", tag=safe_tag, default_value=True)
                dpg.add_text(os.path.basename(p), wrap=180)

def on_proceed_decrypt(sender, app_data):
    selected = []
    for p in STATE.get("imgs_in_folder", []):
        key = f"chk_{hashlib.sha1(str(p).encode()).hexdigest()}"
        try:
            val = dpg.get_value(key)
        except Exception:
            val = True
        if val:
            selected.append(p)
    if not selected:
        dpg.configure_item("error_popup", show=True)
        return
    show_page("loading_processing")
    simulate_progress_and_render("proc_progress", steps=10, delay=0.04)
    STATE["last_paths"] = selected
    show_results(paths=STATE["last_paths"])

# ---------------------------
# Save helpers (revamped to reveal saved files)
# ---------------------------
def on_save_single_image(path):
    pstr = os.path.abspath(str(path)) if path is not None else None
    mapping = STATE.get("display_map", {}).get(pstr) if pstr else None
    if mapping:
        save_src = mapping.get("stego") or mapping.get("decrypted") or mapping.get("original") or pstr
    else:
        save_src = pstr

    if not save_src or not isinstance(save_src, (str, bytes, os.PathLike)) or not os.path.exists(str(save_src)):
        dpg.set_value("info_popup_text", "No valid image file to save. (source missing)")
        dpg.configure_item("info_popup", show=True)
        return

    save_src = str(save_src)
    base = os.path.splitext(os.path.basename(save_src))[0] or "image"
    suggested = base + ("_stego.jpg" if STATE.get("mode") == "encrypt" else "_decrypted.jpg")

    initial_dir = os.path.dirname(save_src) or _default_desktop_dir()
    dest = ask_save_file_jpg(default_name=suggested, initial_dir=initial_dir)
    if not dest:
        return
    ok, msg = save_image_with_conversion(save_src, dest)
    if ok:
        try:
            open_in_explorer_external(dest)
        except Exception:
            pass
    dpg.set_value("info_popup_text", msg)
    dpg.configure_item("info_popup", show=True)

def on_save_folder(sender=None, app_data=None):
    paths = STATE.get("last_paths", []) or []
    if not paths:
        dpg.set_value("info_popup_text", "No images to save.")
        dpg.configure_item("info_popup", show=True)
        return
    dest_folder = ask_save_directory()
    if not dest_folder:
        return

    successes = []
    failures = []
    for p in paths:
        pstr = os.path.abspath(str(p))
        mapping = STATE.get("display_map", {}).get(pstr, {})
        save_src = mapping.get("stego", mapping.get("decrypted", pstr))
        if not save_src or not os.path.exists(str(save_src)):
            failures.append(f"{os.path.basename(pstr)}: source missing")
            continue
        dest = os.path.join(dest_folder, os.path.basename(save_src))
        if os.path.exists(dest):
            name, ext = os.path.splitext(dest)
            dest = f"{name}_{uuid.uuid4().hex[:6]}{ext}"
        ok, msg = save_image_with_conversion(save_src, dest)
        if ok:
            successes.append(os.path.basename(dest))
        else:
            failures.append(f"{os.path.basename(save_src)}: {msg}")

    # Use \n inside a single-line f-string to avoid unterminated-string syntax errors
    summary = f"Saved {len(successes)} images to:\n{dest_folder}"
    if failures:
        summary += "\n\nFailures:\n" + "\n".join(failures)
    dpg.set_value("info_popup_text", summary)
    dpg.configure_item("info_popup", show=True)
    if successes:
        try:
            open_in_explorer_external(dest_folder)
        except Exception:
            pass

# ---------------------------
# Results display (clicking stego/decrypted now offers direct save)
# ---------------------------
def show_results(paths):
    if dpg.does_item_exist("results_container"):
        children = dpg.get_item_children("results_container", 1) or []
        for c in children:
            try:
                dpg.delete_item(c)
            except Exception:
                pass

    STATE["display_map"] = {}

    with dpg.group(parent="results_container"):
        action_word = "encrypted" if STATE["mode"] == "encrypt" else "decrypted"
        dpg.add_text(f"Yay! The Image(s) are now {action_word}.", color=[0,200,0])

        if len(paths) > 1:
            with dpg.group(horizontal=True):
                dpg.add_button(label="Save Folder (save all shown)", callback=on_save_folder)
                dpg.add_spacer(width=8)
                dpg.add_button(label="Open Containing Folder (external)", callback=lambda s,a, p=paths[0]: open_in_explorer_external(os.path.dirname(p)))
                dpg.add_spacer(width=8)
                dpg.add_button(label="Home", callback=on_home_from_results)
        else:
            with dpg.group(horizontal=True):
                dpg.add_button(label="Save Image", callback=lambda s,a, p=paths[0]: on_save_single_image(p))
                dpg.add_spacer(width=8)
                dpg.add_button(label="Reveal (external)", callback=lambda s,a, p=paths[0]: open_in_explorer_external(p))
                dpg.add_spacer(width=8)
                dpg.add_button(label="Home", callback=on_home_from_results)

        dpg.add_separator()

        container_width = 860
        spacing = 18
        cols = 3

        for p in paths:
            pstr = os.path.abspath(str(p))
            # store mapping for later saves. include 'decrypted' key for decrypt mode
            STATE["display_map"][pstr] = {"original": pstr, "blocks": pstr, "stego": pstr, "decrypted": pstr}

            with dpg.child_window(width=container_width, height=300):
                texs, w, h = get_three_side_by_side_textures(pstr, container_width=container_width, spacing=spacing, max_height=220, cols=cols)
                if STATE["mode"] == "encrypt":
                    labels = ["Original", "Blocks (entropy)", "Stego"]
                    view_keys = ["original", "blocks", "stego"]
                else:
                    labels = ["Stego", "Blocks (entropy)", "Decrypted"]
                    view_keys = ["stego", "blocks", "decrypted"]

                with dpg.group(horizontal=True):
                    dpg.add_spacer(width=8)
                    for idx, (tex, lab) in enumerate(zip(texs, labels)):
                        key_for_view = view_keys[idx]
                        with dpg.group(horizontal=False):
                            if tex:
                                def make_view_callback(pp, vkey, vlabel):
                                    def _cb(s, a):
                                        mapping = STATE.get("display_map", {}).get(pp, {})
                                        src = mapping.get(vkey) or mapping.get("stego") or mapping.get("original") or pp
                                        # If user clicked a stego or decrypted view, open Save As immediately
                                        if vkey in ("stego", "decrypted"):
                                            base = os.path.splitext(os.path.basename(src))[0] or "image"
                                            suggested = base + ("_stego.jpg" if vkey == "stego" else "_decrypted.jpg")
                                            initial_dir = os.path.dirname(src) or _default_desktop_dir()
                                            dest = ask_save_file_jpg(default_name=suggested, initial_dir=initial_dir)
                                            if dest:
                                                ok, msg = save_image_with_conversion(src, dest)
                                                if ok:
                                                    try:
                                                        open_in_explorer_external(dest)
                                                    except Exception:
                                                        pass
                                                dpg.set_value("info_popup_text", msg)
                                                dpg.configure_item("info_popup", show=True)
                                        else:
                                            dpg.set_value("info_popup_text", f"Path: {src}\nView: {vlabel}")
                                            dpg.configure_item("info_popup", show=True)
                                    return _cb
                                try:
                                    dpg.add_image_button(tex, width=w, height=h, callback=make_view_callback(pstr, key_for_view, lab))
                                except Exception:
                                    dpg.add_image(tex, width=w, height=h)
                            else:
                                dpg.add_text("(thumbnail missing)")
                            dpg.add_text(lab)
                        if idx != cols - 1:
                            dpg.add_spacer(width=spacing)
                    dpg.add_spacer(width=8)

                # row actions (Save uses mapping stored above)
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Save Image", callback=lambda s,a, pp=pstr: on_save_single_image(pp))
                    dpg.add_spacer(width=8)
                    dpg.add_button(label="Info", callback=lambda s,a, pp=pstr: (dpg.set_value("info_popup_text", f"Path: {pp}"), dpg.configure_item("info_popup", show=True)))
                    dpg.add_spacer(width=8)
                    dpg.add_button(label="Reveal (external)", callback=lambda s,a, pp=pstr: open_in_explorer_external(pp))

    show_page("results")

# ---------------------------
# Open / Home helpers
# ---------------------------
def on_open_in_explorer(sender, app_data):
    paths = STATE.get("last_paths", [])
    if not paths:
        dpg.configure_item("error_no_results", show=True)
        return
    show_results(paths)

def on_home_from_results(sender=None, app_data=None):
    show_page("home")

# ---------------------------
# Password UI behavior
# ---------------------------
def on_password_change(sender, app_data):
    pw = dpg.get_value("pwd_input") or ""
    STATE["password"] = pw
    strong = password_is_strong(pw)
    if strong:
        dpg.set_value("pwd_eval", "Strong")
        try:
            dpg.configure_item("pwd_eval", color=[0, 180, 0])
            dpg.configure_item("btn_hash_password", enabled=True)
        except Exception:
            pass
    else:
        dpg.set_value("pwd_eval", "Weak")
        try:
            dpg.configure_item("pwd_eval", color=[200, 50, 50])
            dpg.configure_item("btn_hash_password", enabled=False)
        except Exception:
            pass

def on_hash_password(sender, app_data):
    pw = dpg.get_value("pwd_input") or ""
    if not password_is_strong(pw):
        dpg.set_value("info_popup_text", "Password is not strong enough. Use at least 12 characters and mix cases, digits, symbols.")
        dpg.configure_item("info_popup", show=True)
        return
    STATE["password"] = pw
    show_page("loading_hash")
    simulate_progress_and_render("hash_progress", steps=10, delay=0.03)
    dpg.set_value("action_success_text", "Yay! Your password looks good. Let us " + ("secure" if STATE["mode"] == "encrypt" else "decrypt") + " images together.")
    show_page("action_success")

# ---------------------------
# Build UI
# ---------------------------
def build_ui():
    dpg.create_context()
    dpg.create_viewport(title="ALMV (Cryptography + Steganography)", width=1000, height=760)

    with dpg.window(tag="main_window", no_title_bar=True, width=1000, height=760, pos=[0,0]):
        with dpg.group(horizontal=True):
            dpg.add_text("ALMV (Cryptography + Steganography)")
            dpg.add_spacer(width=20)
            dpg.add_button(label="☰ Menu", width=90, callback=lambda s,a: dpg.show_item("menu_popup"))
        dpg.add_separator()

        with dpg.child_window(tag="page_home", width=980, height=620):
            register_page("home", "page_home")
            dpg.add_spacer(height=30)
            dpg.add_text("ALMV", tag="home_big")
            dpg.add_text("Cryptography + Steganography")
            dpg.add_spacer(height=10)
            dpg.add_text("The only freeware that secures your image metadata in plain sight.")
            dpg.add_spacer(height=20)
            with dpg.group(horizontal=True):
                dpg.add_button(label="Encrypt Images", width=220, height=44, callback=lambda s,a: on_encrypt_click(s,a))
                dpg.add_spacer(width=20)
                dpg.add_button(label="Decrypt Images", width=220, height=44, callback=lambda s,a: on_decrypt_click(s,a))
            dpg.add_spacer(height=200)

        with dpg.child_window(tag="page_about", width=980, height=620, show=False):
            register_page("about", "page_about")
            dpg.add_text("About ALMV")
            dpg.add_separator()
            dpg.add_text("ALMV is a prototype application combining cryptographic hashing and steganographic metadata protection practices.\n\nThis about page can be expanded with details about your team, research, and methodology.", wrap=900)
            dpg.add_spacer(height=20)
            dpg.add_button(label="Back to Home", callback=lambda s,a: show_page("home"))

        with dpg.child_window(tag="page_password", width=980, height=620, show=False):
            register_page("password", "page_password")
            dpg.add_text("Enter password for your image/s")
            dpg.add_input_text(tag="pwd_input", hint="Password", password=True, width=520, callback=on_password_change)
            dpg.add_button(label="👁️", width=36, callback=lambda s,a: dpg.configure_item("pwd_input", password=not dpg.get_item_configuration("pwd_input")["password"]))
            dpg.add_spacer(height=8)
            dpg.add_button(label="Hash password", tag="btn_hash_password", callback=on_hash_password, enabled=False)
            dpg.add_spacer(width=8)
            dpg.add_button(label="Back", callback=lambda s,a: show_page("home"))
            dpg.add_spacer(height=8)
            dpg.add_text("Password status:", tag="pwd_status_label")
            dpg.add_text("", tag="pwd_eval")
            dpg.add_separator()

        with dpg.child_window(tag="page_action_success", width=980, height=620, show=False):
            register_page("action_success", "page_action_success")
            dpg.add_text("", tag="action_success_text")
            dpg.add_spacer(height=10)
            with dpg.group(horizontal=True):
                dpg.add_button(label="Select a JPG / HEIC image to encrypt/decrypt", tag="btn_select_single", callback=on_select_single)
                dpg.add_spacer(width=10)
                dpg.add_button(label="Select a folder containing JPG / HEIC images", callback=on_select_folder)
            dpg.add_spacer(height=20)
            dpg.add_button(label="Back to Password", callback=lambda s,a: show_page("password"))

        with dpg.child_window(tag="page_loading_hash", width=980, height=620, show=False):
            register_page("loading_hash", "page_loading_hash")
            dpg.add_text("Currently hashing your password...")
            dpg.add_progress_bar(tag="hash_progress", default_value=0.0, width=760)

        with dpg.child_window(tag="page_loading_delay_then_back", width=980, height=620, show=False):
            register_page("loading_delay_then_back", "page_loading_delay_then_back")
            dpg.add_text("", tag="loading_message")
            dpg.add_spacer(height=8)
            dpg.add_text("Returning to password menu shortly...")

        with dpg.child_window(tag="page_loading_processing", width=980, height=620, show=False):
            register_page("loading_processing", "page_loading_processing")
            dpg.add_text("Processing images...")
            dpg.add_progress_bar(tag="proc_progress", default_value=0.0, width=760)

        with dpg.child_window(tag="page_image_selection", width=980, height=620, show=False):
            register_page("image_selection", "page_image_selection")
            dpg.add_text("Do you want to process all images in the folder? Feel free to select those you wish not to include!")
            dpg.add_separator()
            dpg.add_child_window(tag="selection_container", width=940, height=420)
            dpg.add_spacer(height=8)
            with dpg.group(horizontal=True):
                dpg.add_button(label="Proceed", callback=on_proceed_decrypt)
                dpg.add_spacer(width=10)
                dpg.add_button(label="Back", callback=lambda s,a: show_page("action_success"))

        with dpg.child_window(tag="page_results", width=980, height=620, show=False):
            register_page("results", "page_results")
            dpg.add_child_window(tag="results_container", width=940, height=420)
            dpg.add_spacer(height=8)
            with dpg.group(horizontal=True):
                dpg.add_button(label="Information", callback=lambda s,a: dpg.configure_item("info_popup", show=True))
                dpg.add_spacer(width=10)
                dpg.add_button(label="Open (show results)", callback=on_open_in_explorer)
                dpg.add_spacer(width=10)
                dpg.add_button(label="Home", callback=on_home_from_results)

        dpg.add_separator()
        dpg.add_text("Pioneering the future of digital privacy through innovative cryptographic and steganographic research.\nVersion 1 / September 2025")

    with dpg.window(label="Menu", modal=False, show=False, tag="menu_popup", width=200, height=120):
        dpg.add_button(label="Home", callback=lambda s,a: (show_page("home"), dpg.hide_item("menu_popup")))
        dpg.add_button(label="About", callback=lambda s,a: (show_page("about"), dpg.hide_item("menu_popup")))

    with dpg.window(label="Info", modal=True, show=False, tag="info_popup", width=520, height=220):
        dpg.add_text("", tag="info_popup_text", wrap=480)
        dpg.add_spacer(height=8)
        dpg.add_button(label="Close", callback=lambda s,a: dpg.configure_item("info_popup", show=False))
    with dpg.window(label="Error - No images selected", modal=True, show=False, tag="error_popup", width=340, height=160):
        dpg.add_text("No images selected to decrypt.")
        dpg.add_button(label="OK", callback=lambda s,a: dpg.configure_item("error_popup", show=False))
    with dpg.window(label="Error - No results", modal=True, show=False, tag="error_no_results", width=340, height=160):
        dpg.add_text("No results available to open in Explorer.")
        dpg.add_button(label="OK", callback=lambda s,a: dpg.configure_item("error_no_results", show=False))

    show_page("home")

    dpg.setup_dearpygui()
    dpg.show_viewport()
    try:
        dpg.maximize_viewport()
    except Exception:
        try:
            dpg.set_viewport_fullscreen(True)
        except Exception:
            pass
    dpg.start_dearpygui()
    dpg.destroy_context()

# ---------------------------
# Page registry helpers
# ---------------------------
PAGE_IDS = {}
def register_page(name, dpg_id):
    PAGE_IDS[name] = dpg_id

def show_page(name):
    for k, v in PAGE_IDS.items():
        try:
            if dpg.does_item_exist(v):
                if k == name:
                    dpg.show_item(v)
                else:
                    dpg.hide_item(v)
        except Exception:
            pass

# ---------------------------
# Navigation callbacks
# ---------------------------
def on_encrypt_click(sender, app_data):
    STATE["mode"] = "encrypt"
    try:
        dpg.set_value("pwd_input", "")
        dpg.set_value("pwd_eval", "")
    except Exception:
        pass
    try:
        dpg.configure_item("btn_hash_password", enabled=False)
    except Exception:
        pass
    show_page("password")

def on_decrypt_click(sender, app_data):
    STATE["mode"] = "decrypt"
    try:
        dpg.set_value("pwd_input", "")
        dpg.set_value("pwd_eval", "")
    except Exception:
        pass
    try:
        dpg.configure_item("btn_hash_password", enabled=False)
    except Exception:
        pass
    show_page("password")

# ---------------------------
# Start
# ---------------------------
if __name__ == "__main__":
    build_ui()
