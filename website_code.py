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

def get_images(folder):
    return [
        f for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f))
        and f.lower().endswith((".png",".jpg",".jpeg",".gif",".webp"))
    ]

metadata_file = os.path.join(base_dir,"image_data.json")
if os.path.exists(metadata_file):
    with open(metadata_file,"r",encoding="utf-8") as f:
        try:
            image_metadata = json.load(f)
        except:
            image_metadata = {}
else:
    image_metadata = {}

def get_meta(path):
    meta = image_metadata.get(path.replace("\\","/"),{})
    title = meta.get("title",os.path.splitext(os.path.basename(path))[0])
    desc = meta.get("description","")
    return title,desc

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
.gallery-img{
width:100%;
height:300px;
object-fit:cover;
border-radius:6px;
cursor:pointer;
}
.gallery-img:hover{
transform:scale(1.05);
transition:.3s;
}
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
left:50%;
transform:translateX(-50%);
color:white;
background:rgba(0,0,0,.45);
padding:10px 20px;
border-radius:6px;
text-align:center;
bottom:20px;
}
.lightbox{
display:none;
position:fixed;
top:0;
left:0;
width:100%;
height:100%;
background:rgba(0,0,0,.85);
backdrop-filter:blur(6px);
justify-content:center;
align-items:center;
z-index:9999;
}
.lightbox img{
max-width:90%;
max-height:90%;
}
.arrow{
position:absolute;
top:50%;
font-size:3rem;
color:white;
cursor:pointer;
user-select:none;
padding:10px;
}
.arrow.left{left:15px;}
.arrow.right{right:15px;}
</style>
"""

lightbox_script = """
<script>
let galleryImages=[]
let currentIndex=0
function openLightbox(el){
galleryImages=[...document.querySelectorAll('.gallery-img')]
currentIndex=galleryImages.indexOf(el)
updateLightbox()
document.getElementById('lightbox').style.display='flex'
}
function closeLightbox(){
document.getElementById('lightbox').style.display='none'
}
function updateLightbox(){
const img=document.getElementById('lightbox-img')
img.src=galleryImages[currentIndex].src
}
function prevImage(e){
e.stopPropagation()
currentIndex=(currentIndex-1+galleryImages.length)%galleryImages.length
updateLightbox()
}
function nextImage(e){
e.stopPropagation()
currentIndex=(currentIndex+1)%galleryImages.length
updateLightbox()
}
</script>
"""

lightbox_html = """
<div id="lightbox" class="lightbox" onclick="closeLightbox()">
<span class="arrow left" onclick="prevImage(event)">&#10094;</span>
<img id="lightbox-img">
<span class="arrow right" onclick="nextImage(event)">&#10095;</span>
</div>
"""

def generate_website():
    # Update metadata for new images
    all_folders = [paths["home"]] + list(gallery_folders.values())
    for folder in all_folders:
        for img in get_images(folder):
            img_path = os.path.join(folder,img).replace("\\","/")
            if img_path not in image_metadata:
                image_metadata[img_path]={"title":"","description":""}
    with open(metadata_file,"w",encoding="utf-8") as f:
        json.dump(image_metadata,f,indent=4)

    # Home Page
    home_images = get_images(paths["home"])
    hero_image = "web_images/home_file/Royal Archway.jpg"  # Set hero image

    home_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Waza Photography</title>
{bootstrap}
{styles}
{lightbox_script}
</head>
<body>
{navbar}
<header class="hero">
<img src="{hero_image}" loading="eager">
<div class="hero-text">
<a href="gallery.html" class="banner-text">Explore the Gallery</a>
</div>
</header>
<section class="container my-5">
<h2 class="text-center mb-4">Featured Images</h2>
<div class="row g-3">
"""

    for img in home_images:
        img_path = f"web_images/home_file/{img}"
        title,desc = get_meta(img_path)
        home_html += f"""
<div class="col-md-4">
<sl-card>
<img src="{img_path}" class="gallery-img"
loading="lazy"
decoding="async"
onclick="openLightbox(this)"
alt="{title}">
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
<footer class="text-center text-muted py-4 bg-light">
<p>&copy; 2026 Warren Eyles</p>
</footer>
{lightbox_html}
</body>
</html>
"""
    with open(os.path.join(base_dir,"index.html"),"w",encoding="utf-8") as f:
        f.write(home_html)

    # Gallery Page
    gallery_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Gallery</title>
{bootstrap}
{styles}
{lightbox_script}
</head>
<body>
{navbar}
"""
    for name,folder in gallery_folders.items():
        images = get_images(folder)
        gallery_html += f"""
<section class="container my-5">
<h2>{name}</h2>
<div class="row g-3">
"""
        folder_name = folder.split(os.sep)[-1]
        for img in images:
            img_path = f"web_images/gallery_images/gallery_themes/{folder_name}/{img}"
            title,desc = get_meta(img_path)
            gallery_html += f"""
<div class="col-md-4">
<sl-card>
<img src="{img_path}" class="gallery-img"
loading="lazy"
decoding="async"
onclick="openLightbox(this)"
alt="{title}">
<div class="card-body">
<h5>{title}</h5>
<p>{desc}</p>
</div>
</sl-card>
</div>
"""
        gallery_html += "</div></section>"

    gallery_html += f"""
<footer class="text-start p-3" style="color:#666;">
&copy; 2026 Waza Photography
</footer>
{lightbox_html}
</body>
</html>
"""
    with open(os.path.join(base_dir,"gallery.html"),"w",encoding="utf-8") as f:
        f.write(gallery_html)

    # Git push
    try:
        subprocess.run(["git","add","."],check=True)
        subprocess.run(["git","commit","-m","Auto update website"],check=True)
        subprocess.run(["git","push"],check=True)
    except:
        pass

class Watcher(FileSystemEventHandler):
    def on_modified(self,event):
        if event.src_path.lower().endswith((".jpg",".jpeg",".png",".gif",".webp")):
            generate_website()

generate_website()

observer = Observer()
observer.schedule(Watcher(), path=paths["main"], recursive=True)
observer.start()

print("Watching for changes")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()