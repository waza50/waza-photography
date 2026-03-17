import os
import json
import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# =========================================================
# 1. PROJECT PATHS (edit if you move folders)
# =========================================================
base_dir = os.path.dirname(__file__)

paths = {
    "main": os.path.join(base_dir, "web_images"),
    "home": os.path.join(base_dir, "web_images", "home_file"),
    "themes": os.path.join(base_dir, "web_images", "gallery_images", "gallery_themes")
}

# =========================================================
# 2. THEMES (add/remove themes here)
# =========================================================
themes = {
    "nature": {
        "home": os.path.join(paths["themes"], "nature_home"),
        "gallery": os.path.join(paths["themes"], "nature_gallery")
    },
    "landscape": {
        "home": os.path.join(paths["themes"], "landscape_home"),
        "gallery": os.path.join(paths["themes"], "landscape_gallery")
    },
    "portraiture": {
        "home": os.path.join(paths["themes"], "portraiture_home"),
        "gallery": os.path.join(paths["themes"], "portraiture_gallery")
    }
}

# =========================================================
# 3. IMAGE METADATA (titles and descriptions)
# =========================================================
metadata_file = os.path.join(base_dir, "image_data.json")

if os.path.exists(metadata_file):
    with open(metadata_file, "r", encoding="utf-8") as f:
        try:
            image_metadata = json.load(f)
        except:
            image_metadata = {}
else:
    image_metadata = {}

def get_images(folder):
    if not os.path.exists(folder):
        print("Missing folder:", folder)
        return []

    return [
        f for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f))
        and f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
    ]
def get_meta(path):
    meta = image_metadata.get(path.replace("\\", "/"), {})
    title = meta.get("title", os.path.splitext(os.path.basename(path))[0])
    desc = meta.get("description", "")
    return title, desc

# =========================================================
# 4. UI COMPONENTS 
# =========================================================

# Navbar links
navbar = """
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
<div class="container-fluid">
<ul class="navbar-nav me-auto">
<li class="nav-item"><a class="nav-link" href="index.html">Home</a></li>
<li class="nav-item"><a class="nav-link" href="gallery.html">Gallery</a></li>
<li class="nav-item"><a class="nav-link" href="about.html">About</a></li>
<li class="nav-item"><a class="nav-link" href="contact.html">Contact</a></li>
</ul>
</div>
</nav>
"""

# External libraries
bootstrap = """
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<script type="module" src="https://cdn.jsdelivr.net/npm/@shoelace-style/shoelace@2/dist/shoelace.js"></script>
"""

# Styles
styles = """
<style>
.gallery-img{
width:100%;
height:250px;
object-fit:cover;
border-radius:6px;
}
</style>
"""

# =========================================================
# 5. GENERATE WEBSITE
# =========================================================
def generate_website():

    # Ensure metadata exists for all images
    all_folders = [paths["home"]]
    for t in themes.values():
        all_folders.append(t["home"])
        all_folders.append(t["gallery"])

    for folder in all_folders:
        for img in get_images(folder):
            path = os.path.join(folder, img).replace("\\", "/")
            if path not in image_metadata:
                image_metadata[path] = {"title": "", "description": ""}

    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(image_metadata, f, indent=4)

    # =====================================================
    # 6. HOME PAGE 
    # =====================================================
    home_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Waza Photography</title>
{bootstrap}
{styles}
</head>
<body>
{navbar}

<section class="container my-5">
<h2 class="text-center mb-5">Explore My Work</h2>

<div class="row g-4">
"""

    # Theme preview section (image + button)
    for theme_name, data in themes.items():
        images = get_images(data["home"])
        if not images:
            continue

        img = images[0]
        img_path = f"web_images/gallery_images/gallery_themes/{theme_name}_home/{img}"
        title = theme_name.capitalize()

        home_html += f"""
<div class="col-md-4">
<div class="row align-items-center">

<div class="col-md-6">
<img src="{img_path}" class="gallery-img">
</div>

<div class="col-md-6">
<h4>{title}</h4>
<a href="{theme_name}.html" class="btn btn-dark mt-2">
View {title}
</a>
</div>

</div>
</div>
"""

    home_html += """
</div>
</section>
</body>
</html>
"""

    with open(os.path.join(base_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(home_html)

    # =====================================================
    # 7. INDIVIDUAL THEME PAGES
    # =====================================================
    for theme_name, data in themes.items():

        html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{theme_name.capitalize()}</title>
{bootstrap}
{styles}
</head>
<body>
{navbar}

<section class="container my-5">
<h2 class="text-center mb-4">{theme_name.capitalize()}</h2>

<div class="row g-3">
"""

        images = get_images(data["gallery"])

        for img in images:
            folder = f"{theme_name}_gallery"
            img_path = f"web_images/gallery_images/gallery_themes/{folder}/{img}"

            title, desc = get_meta(img_path)

            html += f"""
<div class="col-md-4">
<sl-card>
<img src="{img_path}" class="gallery-img">
<div class="card-body">
<h5>{title}</h5>
<p>{desc}</p>
</div>
</sl-card>
</div>
"""

        html += """
</div>
</section>
</body>
</html>
"""

        with open(os.path.join(base_dir, f"{theme_name}.html"), "w", encoding="utf-8") as f:
            f.write(html)

    # =====================================================
    # 8. MAIN GALLERY PAGE (simple theme selector)
    # =====================================================
    gallery_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Gallery</title>
{bootstrap}
</head>
<body>
{navbar}

<section class="container my-5 text-center">
<h2>Select a Theme</h2>
"""

    for theme_name in themes:
        gallery_html += f"""
<a href="{theme_name}.html" class="btn btn-dark m-2">
{theme_name.capitalize()}
</a>
"""

    gallery_html += """
</section>
</body>
</html>
"""

    with open(os.path.join(base_dir, "gallery.html"), "w", encoding="utf-8") as f:
        f.write(gallery_html)

    # =====================================================
    # 9. AUTO GIT PUSH (optional)
    # =====================================================
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Auto update"], check=True)
        subprocess.run(["git", "push"], check=True)
    except:
        pass

# =========================================================
# 10. WATCHDOG (auto update on image change)
# =========================================================
class Watcher(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.lower().endswith((".jpg", ".png", ".jpeg", ".webp")):
            generate_website()

generate_website()

observer = Observer()
observer.schedule(Watcher(), path=paths["main"], recursive=True)
observer.start()

print("Watching for changes...")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()