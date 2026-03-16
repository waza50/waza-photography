import os
import json
import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

base_dir = os.path.dirname(__file__)
paths = {
    "main": os.path.join(base_dir, "web_images"),
    "home": os.path.join(base_dir, "web_images", "home_file"),
    "gallery": os.path.join(base_dir, "web_images", "gallery_images")
}
paths["themes"] = os.path.join(paths["gallery"], "gallery_themes")

gallery_folders = {
    "Nature": os.path.join(paths["themes"], "nature_file"),
    "Landscape": os.path.join(paths["themes"], "landscape_file"),
    "Portraiture": os.path.join(paths["themes"], "portraiture_file")
}

errors = {
    paths["main"]: "Error 502",
    paths["home"]: "Error 503",
    paths["gallery"]: "Error 504",
    paths["themes"]: "Error 505",
    gallery_folders["Nature"]: "Error 506",
    gallery_folders["Landscape"]: "Error 507",
    gallery_folders["Portraiture"]: "Error 508"
}

for folder, msg in errors.items():
    if not os.path.exists(folder):
        input(msg)
        exit()

def get_images(folder):
    return [
        f for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f))
        and f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))
    ]

metadata_file = os.path.join(base_dir, "image_data.json")
if os.path.exists(metadata_file):
    with open(metadata_file, "r", encoding="utf-8") as f:
        image_metadata = json.load(f)
else:
    image_metadata = {}

def get_meta(path):
    meta = image_metadata.get(path.replace("\\","/"), {})
    title = meta.get("title", os.path.splitext(os.path.basename(path))[0])
    desc = meta.get("description","")
    return title, desc

navbar = """
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
<div class="container-fluid">
<ul class="navbar-nav me-auto mb-2 mb-lg-0">
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

gallery_css = """
<style>
.gallery-img{
width:100%;
height:300px;
object-fit:cover;
border-radius:6px;
cursor:pointer;
}
.gallery-img:hover{
transform:scale(1.05);
transition:0.3s;
}
.lightbox {
display:none;
position:fixed;
top:0;left:0;width:100%;height:100%;
background:rgba(0,0,0,0.8);
backdrop-filter:blur(5px);
justify-content:center;
align-items:center;
z-index:9999;
}
.lightbox img {
max-width:90%;
max-height:90%;
border-radius:6px;
}
</style>
<script>
function openLightbox(el){
    const lightbox = document.getElementById('lightbox');
    lightbox.style.display='flex';
    lightbox.querySelector('img').src=el.src;
}
function closeLightbox(){document.getElementById('lightbox').style.display='none';}
</script>
"""

lightbox_modal = """
<div id="lightbox" class="lightbox" onclick="closeLightbox()">
<img src="" alt="Lightbox Image">
</div>
"""

def generate_website():
    all_folders = [paths["home"]] + list(gallery_folders.values())
    for folder in all_folders:
        for img in get_images(folder):
            img_path = os.path.join(folder, img).replace("\\", "/")
            if img_path not in image_metadata:
                image_metadata[img_path] = {"title": "", "description": ""}
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(image_metadata, f, indent=4)

    home_images = get_images(paths["home"])
    home_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Waza Photography</title>
{bootstrap}
{gallery_css}
</head>
<body>
{navbar}
<header class="text-center text-white bg-dark py-5">
<h1>Waza Photography</h1>
<p>Discover the captivating world of Waza Photography.</p>
</header>
<section class="container my-5">
<h2 class="text-center mb-4">Featured Images</h2>
<div class="row g-3">
"""
    for img in home_images:
        img_path = f"web_images/home_file/{img}"
        title, desc = get_meta(img_path)
        home_html += f"""
    <div class="col-md-4">
    <sl-card>
    <img src="{img_path}" class="gallery-img" alt="{title}" title="{desc}" onclick="openLightbox(this)">
    <div class="card-body">
    <h5>{title}</h5>
    <p>{desc}</p>
    </div>
    </sl-card>
    </div>
        """
    home_html += "</div></section><footer class='text-center text-muted py-4 bg-light'><p>&copy; 2026 Warren Eyles</p></footer>"
    home_html += lightbox_modal
    home_html += "</body></html>"

    with open(os.path.join(base_dir,"index.html"),"w",encoding="utf-8") as f:
        f.write(home_html)

    gallery_data = {name: get_images(folder) for name, folder in gallery_folders.items()}

    def generate_gallery_section(name, images, folder):
        section = f'<section class="container my-5"><h2>{name}</h2><div class="row g-3">'
        folder_name = folder.split(os.sep)[-1]
        for img in images:
            img_path = f"web_images/gallery_images/gallery_themes/{folder_name}/{img}"
            title, desc = get_meta(img_path)
            section += f"""
        <div class="col-md-4">
        <sl-card>
        <img src="{img_path}" class="gallery-img" alt="{title}" title="{desc}" onclick="openLightbox(this)">
        <div class="card-body">
        <h5>{title}</h5>
        <p>{desc}</p>
        </div>
        </sl-card>
        </div>
            """
        section += "</div></section>"
        return section

    gallery_sections = ""
    for name, images in gallery_data.items():
        if images:
            gallery_sections += generate_gallery_section(name, images, gallery_folders[name])

    gallery_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Gallery</title>
{bootstrap}
{gallery_css}
</head>
<body>
{navbar}
{gallery_sections}
<footer class="text-start p-3" style="color:#666;">&copy; 2026 Waza Photography</footer>
{lightbox_modal}
</body>
</html>"""

    with open(os.path.join(base_dir,"gallery.html"),"w",encoding="utf-8") as f:
        f.write(gallery_html)

    about_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>About</title>
{bootstrap}
</head>
<body>
{navbar}
<section class="container my-5">
<h2>About Waza Photography</h2>
<p>Welcome to Waza Photography. Here you will find a collection of images capturing nature, landscapes, and portrait photography.</p>
</section>
<footer class="text-center text-muted py-4 bg-light">
<p>&copy; 2026 Warren Eyles</p>
</footer>
</body>
</html>"""

    with open(os.path.join(base_dir,"about.html"),"w",encoding="utf-8") as f:
        f.write(about_html)

    try:
        subprocess.run(["git","add","."], check=True)
        subprocess.run(["git","commit","-m","Auto update website"], check=True)
        subprocess.run(["git","push"], check=True)
    except:
        print("No changes to push.")

class GalleryWatcher(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.lower().endswith((".jpg",".jpeg",".png",".gif")):
            print(f"Change detected: {event.src_path}")
            generate_website()

generate_website()

observer = Observer()
observer.schedule(GalleryWatcher(), path=paths["main"], recursive=True)
observer.start()
print("Watching for image changes... Press Ctrl+C to stop.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()