import re, os

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
BASE_URL = "https://content.strategiclabpartners.com"

# 1. Fix canonical tags in each slug/index.html
for slug in SLUGS:
    path = os.path.join(BASE, slug, "index.html")
    if not os.path.exists(path):
        print(f"✗ Not found: {path}")
        continue
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    old = f'href="{BASE_URL}/faqs/{slug}"'
    new = f'href="{BASE_URL}/faqs/{slug}/"'
    if old in content:
        content = content.replace(old, new)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✓ Canonical fixed: {slug}/")
    else:
        print(f"? Canonical not in expected format: {slug}")

# 2. Fix links in faqs/index.html
index_path = os.path.join(BASE, "index.html")
if os.path.exists(index_path):
    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()
    for slug in SLUGS:
        for old, new in [
            (f"/faqs/{slug}.html", f"/faqs/{slug}/"),
            (f'"/faqs/{slug}"', f'"/faqs/{slug}/"'),
            (f"'/faqs/{slug}'", f"'/faqs/{slug}/'"),
        ]:
            if old in content:
                content = content.replace(old, new)
                print(f"✓ Link fixed in index: {old} → {new}")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✓ faqs/index.html updated")

print("Done.")
