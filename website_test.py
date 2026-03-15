import os
import time
from threading import Timer
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# -------------------------------------------------
# Waza Photography Website Generator
# -------------------------------------------------

base_dir = os.path.dirname(__file__)

# -----------------------------
# Project directories
# -----------------------------
main_file = os.path.join(base_dir, "web_images")
home_file = os.path.join(base_dir, "web_images", "home_file")
gallery_file = os.path.join(base_dir, "web_images", "gallery_images")
gallery_themes = os.path.join(gallery_file, "gallery_themes")
gallery_themes_nature_file = os.path.join(gallery_themes, "nature_file")
gallery_themes_landscape_file = os.path.join(gallery_themes, "landscape_file")
gallery_themes_portrait_file = os.path.join(gallery_themes, "portraiture_file")

# -----------------------------
# Folder existence checks
# -----------------------------
folders = [
    (main_file, "Error 502: web_images folder missing"),
    (home_file, "Error 503: home_file folder missing"),
    (gallery_file, "Error 504: gallery_images folder missing"),
    (gallery_themes, "Error 508: gallery_themes folder missing"),
    (gallery_themes_nature_file, "Error 505: nature_file missing"),
    (gallery_themes_landscape_file, "Error 506: landscape_file missing"),
    (gallery_themes_portrait_file, "Error 507: portraiture_file missing")
]

for path, error_msg in folders:
    if not os.path.exists(path):
        input(error_msg)
        exit()

# -----------------------------
# Function to get image files
# -----------------------------
def get_images(folder):
    return [
        f for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f)) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
    ]

# -----------------------------
# Site and asset data
# -----------------------------
site_data = {
    "title": "Waza Photography",
    "description": "Discover the captivating world of Waza Photography. Explore stunning photos capturing nature, landscapes, and more."
}

assets_data = {
    "favicon": "https://waza.photography/favicon.ico",
    "stylesheet": "https://waza.photography/styles.css",
    "scripts": ["https://waza.photography/scripts.js"],
    "viewport": "width=device-width, initial-scale=1.0"
}

# -----------------------------
# HTML regeneration function
# -----------------------------
def regenerate_html():
    print("Regenerating HTML pages...")
    # Scan image folders
    home_images = get_images(home_file)
    gallery_nature = get_images(gallery_themes_nature_file)
    gallery_landscape = get_images(gallery_themes_landscape_file)
    gallery_portrait = get_images(gallery_themes_portrait_file)

    # -----------------------------
    # index.html
    # -----------------------------
    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="{assets_data['viewport']}">
    <meta name="description" content="{site_data['description']}">
    <link rel="icon" href="{assets_data['favicon']}">
    <title>{site_data['title']}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@shoelace-style/shoelace@2/dist/themes/light.css">
</head>
<body>

<!-- Navbar -->
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
  <div class="container-fluid">
    <a class="navbar-brand" href="#"></a>
    <div class="collapse navbar-collapse">
      <ul class="navbar-nav me-auto mb-2 mb-lg-0">
        <li class="nav-item"><a class="nav-link" href="index.html">Home</a></li>
        <li class="nav-item"><a class="nav-link" href="gallery.html">Gallery</a></li>
        <li class="nav-item"><a class="nav-link" href="about.html">About</a></li>
        <li class="nav-item"><a class="nav-link" href="contact.html">Contact</a></li>
      </ul>
    </div>
  </div>
</nav>

<!-- Hero Section -->
<header class="hero text-center text-white bg-dark py-5">
    <h1>{site_data['title']}</h1>
    <p>{site_data['description']}</p>
</header>

<!-- Featured Home Images Section -->
<section class="container my-5">
    <h2 class="text-center mb-4">Featured Home Images</h2>
    <div class="row g-3">
"""
    for i, img in enumerate(home_images):
        index_html += f"""
        <div class="col-sm-6 col-md-4 col-lg-3">
            <img src="web_images/home_file/{img}" class="img-fluid rounded" alt="Home Image {i+1}">
        </div>
        """
    index_html += """
    </div>
</section>

<!-- Footer -->
<footer class="text-center text-muted py-4 bg-light">
    <p>© 2026 Warren Eyles</p>
</footer>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script type="module" src="https://cdn.jsdelivr.net/npm/@shoelace-style/shoelace@2/dist/shoelace.js"></script>
</body>
</html>
"""
    with open(os.path.join(base_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

    # -----------------------------
    # gallery.html
    # -----------------------------
    gallery_sections = ""

    def add_gallery_section(title, images, folder):
        nonlocal gallery_sections
        if images:
            gallery_sections += f'<section class="container my-5">\n<h2>{title}</h2>\n<div class="row g-3">\n'
            for i, img in enumerate(images):
                gallery_sections += f'''
        <div class="col-sm-6 col-md-4 col-lg-3">
            <sl-card>
                <img src="{folder}/{img}" class="img-fluid" alt="{title} {i+1}">
            </sl-card>
        </div>
                '''
            gallery_sections += "</div>\n</section>\n"

    add_gallery_section("Nature", gallery_nature, "web_images/gallery_images/gallery_themes/nature_file")
    add_gallery_section("Landscape", gallery_landscape, "web_images/gallery_images/gallery_themes/landscape_file")
    add_gallery_section("Portraiture", gallery_portrait, "web_images/gallery_images/gallery_themes/portraiture_file")

    gallery_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="{assets_data['viewport']}">
    <title>Gallery</title>
    <link rel="icon" href="{assets_data['favicon']}">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script type="module" src="https://cdn.jsdelivr.net/npm/@shoelace-style/shoelace@2/dist/shoelace.js"></script>
</head>
<body>
<!-- Navbar -->
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
  <div class="container-fluid">
    <a class="navbar-brand" href="#"></a>
    <div class="collapse navbar-collapse">
      <ul class="navbar-nav me-auto mb-2 mb-lg-0">
        <li class="nav-item"><a class="nav-link" href="index.html">Home</a></li>
        <li class="nav-item"><a class="nav-link" href="gallery.html">Gallery</a></li>
        <li class="nav-item"><a class="nav-link" href="about.html">About</a></li>
        <li class="nav-item"><a class="nav-link" href="contact.html">Contact</a></li>
      </ul>
    </div>
  </div>
</nav>

{gallery_sections}

<footer class="text-start p-3" style="color:#666;">
&copy; 2026 Waza Photography
</footer>
</body>
</html>
"""
    with open(os.path.join(base_dir, "gallery.html"), "w", encoding="utf-8") as f:
        f.write(gallery_html)

    # -----------------------------
    # about.html
    # -----------------------------
    about_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="{assets_data['viewport']}">
    <title>About</title>
    <link rel="icon" href="{assets_data['favicon']}">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
<!-- Navbar -->
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
  <div class="container-fluid">
    <a class="navbar-brand" href="#"></a>
    <div class="collapse navbar-collapse">
      <ul class="navbar-nav me-auto mb-2 mb-lg-0">
        <li class="nav-item"><a class="nav-link" href="index.html">Home</a></li>
        <li class="nav-item"><a class="nav-link" href="gallery.html">Gallery</a></li>
        <li class="nav-item"><a class="nav-link" href="about.html">About</a></li>
        <li class="nav-item"><a class="nav-link" href="contact.html">Contact</a></li>
      </ul>
    </div>
  </div>
</nav>

<section class="container my-5">
  <h2>About Waza Photography</h2>
  <p>Welcome to Waza Photography! Here you will find stunning images of nature, landscapes, and portraits.</p>
</section>

<footer class="text-center text-muted py-4 bg-light">
    <p>© 2026 Warren Eyles</p>
</footer>
</body>
</html>
"""
    with open(os.path.join(base_dir, "about.html"), "w", encoding="utf-8") as f:
        f.write(about_html)

    print("All HTML pages regenerated!")

# -----------------------------
# Run once to generate initial HTML
# -----------------------------
regenerate_html()

# -----------------------------
# Debounced Watchdog Handler
# -----------------------------
class DebouncedImageFolderHandler(FileSystemEventHandler):
    def __init__(self, delay=1.0):
        super().__init__()
        self.delay = delay
        self.timer = None

    def on_any_event(self, event):
        if not event.is_directory:
            print(f"Change detected: {event.src_path}")
            if self.timer:
                self.timer.cancel()
            self.timer = Timer(self.delay, regenerate_html)
            self.timer.start()

# -----------------------------
# Set up Observer
# -----------------------------
folders_to_watch = [
    home_file,
    gallery_themes_nature_file,
    gallery_themes_landscape_file,
    gallery_themes_portrait_file
]

observer = Observer()
handler = DebouncedImageFolderHandler(delay=1.0)  # 1 second debounce

for folder in folders_to_watch:
    observer.schedule(handler, folder, recursive=True)

observer.start()
print("Watching folders for changes... Press Ctrl+C to stop.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()