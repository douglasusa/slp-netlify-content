import os, shutil

SLUGS = [
    "how-medical-fulfillment-supports-distributed-healthcare-networks",
    "why-standardized-logistics-are-essential-for-medical-programs",
    "how-medical-fulfillment-improves-accuracy-and-reliability",
    "how-medical-kitting-supports-multi-site-healthcare-organizations",
    "why-standardized-kits-are-important-for-healthcare-providers",
    "what-is-slp-connect",
    "how-does-slp-connect-support-program-visibility",
    "decentralized-at-home-collections",
    "sample-integrity-genomics-transcriptomics-proteomics-metabolomics",
]

BASE = "static/faqs"

for slug in SLUGS:
    src = os.path.join(BASE, f"{slug}.html")
    dst_dir = os.path.join(BASE, slug)
    dst = os.path.join(dst_dir, "index.html")
    if os.path.exists(src):
        os.makedirs(dst_dir, exist_ok=True)
        shutil.copy2(src, dst)
        os.remove(src)
        print(f"✓ {slug}.html → {slug}/index.html")
    elif os.path.exists(dst):
        print(f"✓ Already a folder: {slug}/index.html")
    else:
        print(f"✗ Not found: {src}")
