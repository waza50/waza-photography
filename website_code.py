import os
import json
import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# =========================================================
# 1. PATHS
# =========================================================
base_dir = os.path.dirname(__file__)

paths = {
    "main": os.path.join(base_dir, "web_images"),
    "home": os.path.join(base_dir, "web_images", "home_file"),
    "themes": os.path.join(base_dir, "web_images", "gallery_images", "gallery_themes")
}

# =========================================================
# 2. THEMES
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
# 3. METADATA
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
    return meta.get("title", os.path.basename(path)), meta.get("description", "")

# =========================================================
# 4. UI
# =========================================================
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

bootstrap = """
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<script type="module" src="https://cdn.jsdelivr.net/npm/@shoelace-style/shoelace@2/dist/shoelace.js"></script>
"""

styles = """
<style>
<style>
.gallery-img{
  width:100%;
  height:300px;      /* All images same height */
  object-fit:cover;   /* Keeps aspect ratio, crops if necessary */
  border-radius:6px;
  margin-bottom:10px;
}
</style>
.hero{
position:relative;
height:70vh;
overflow:hidden;
}
.hero img{
width:100%;
height:100%;
object-fit:cover;
}
.hero-text{
position:absolute;
top:50%;
left:50%;
transform:translate(-50%,-50%);
color:white;
background:rgba(0,0,0,.45);
padding:25px;
border-radius:6px;
text-align:center;
}
.banner{
position:relative;
height:40vh;
margin:50px 0;
overflow:hidden;
border-radius:6px;
}
.banner img{
width:100%;
height:100%;
object-fit:cover;
opacity:0.8;
}
.banner-text{
position:absolute;
top:50%;
left:50%;
transform:translate(-50%,-50%);
color:white;
font-size:2rem;
text-align:center;
background:rgba(0,0,0,0.45);
padding:15px;
border-radius:6px;
}
</style>
"""

# =========================================================
# 5. GENERATE WEBSITE
# =========================================================
def generate_website():

    # --------------------------
    # METADATA AUTO-FILL
    # --------------------------
    for t in themes.values():
        for folder in [t["home"], t["gallery"]]:
            for img in get_images(folder):
                full_path = os.path.join(folder, img).replace("\\", "/")
                if full_path not in image_metadata:
                    image_metadata[full_path] = {"title": "", "description": ""}

    with open(metadata_file, "w") as f:
        json.dump(image_metadata, f, indent=4)

    # =====================================================
    # HOME PAGE
    # =====================================================
    home_images = get_images(paths["home"])
    hero_image = os.path.join(paths["home"], "Royal Archway.jpg")
    hero_rel = os.path.relpath(hero_image, base_dir).replace("\\", "/")

    home_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Waza Photography</title>
{bootstrap}
{styles}
</head>
<body>
{navbar}

<header class="hero">
<img src="{hero_rel}" loading="eager">
<div class="hero-text">
<h1>Waza Photography</h1>
<h2>Explore the world through my lens</h2>
<p>Discover the captivating world of Waza Photography</p>
</div>
</header>

<section class="container my-5">
<h3 class="text-center mb-4">Featured Images</h3>
<div class="row g-3">
"""

    for img in home_images:
        img_path = os.path.join(paths["home"], img)
        rel_path = os.path.relpath(img_path, base_dir).replace("\\", "/")
        title, desc = get_meta(img_path)
        home_html += f"""
<div class="col-md-4">
<sl-card>
<img src="{rel_path}" class="gallery-img" loading="lazy" decoding="async" alt="{title}">
<div class="card-body">
<h5>{title}</h5>
<p>{desc}</p>
</div>
</sl-card>
</div>
"""

    home_html += f"""
</div>
</section>

<section class="banner">
<img src="{hero_rel}">
<div class="banner-text">Explore the Gallery</div>
<a href="gallery.html" class="banner-text">Explore the Gallery</a>
</section>

<footer class="text-center text-muted py-4 bg-light">
<p>&copy; 2026 Warren Eyles</p>
</footer>
</body>
</html>
"""

    with open(os.path.join(base_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(home_html)

    # =====================================================
    # THEME PAGES
    # =====================================================
    for theme_name, data in themes.items():
        html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{theme_name}</title>
{bootstrap}
{styles}
</head>
<body>
{navbar}
<section class="container my-5">
<div class="row g-3">
"""
        for img in get_images(data["gallery"]):
            full_path = os.path.join(data["gallery"], img)
            rel_path = os.path.relpath(full_path, base_dir).replace("\\", "/")
            title, desc = get_meta(full_path)
            html += f"""
<div class="col-md-4">
<img src="{rel_path}" class="gallery-img">
<h5>{title}</h5>
</div>
"""
        html += "</div></section></body></html>"

        with open(os.path.join(base_dir, f"{theme_name}.html"), "w") as f:
            f.write(html)

    # =====================================================
    # GALLERY PAGE (updated layout)
    # =====================================================
    gallery_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Gallery</title>
{bootstrap}
{styles}
</head>
<body>
{navbar}
<section class="container my-5">
<div class="row g-5">
"""

    for theme_name, data in themes.items():
        images = get_images(data["home"])
        if not images:
            continue
        img = images[0]
        full_path = os.path.join(data["home"], img)
        rel_path = os.path.relpath(full_path, base_dir).replace("\\", "/")
        title = theme_name.capitalize()
        gallery_html += f"""
<div class="col-12 mb-5">
<div class="row align-items-center">
<div class="col-md-6">
<img src="{rel_path}" class="gallery-img">
</div>
<div class="col-md-6">
<h3>{title}</h3>
<a href="{theme_name}.html" class="btn btn-dark mt-2">View {title}</a>
</div>
</div>
</div>
"""

    gallery_html += "</div></section></body></html>"

    with open(os.path.join(base_dir, "gallery.html"), "w", encoding="utf-8") as f:
        f.write(gallery_html)

    # =====================================================
    # AUTO GITHUB PUSH
    # =====================================================
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Auto update website"], check=True)
        subprocess.run(["git", "push"], check=True)
    except:
        pass

# =========================================================
# WATCHDOG
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