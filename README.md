# SLP CONNECT™ Content Hub  
Static content repository for Netlify deployment

This repository contains the complete static version of the SLP CONNECT™ Content Hub.  
All public-facing content is served directly from the `/static/` directory.

---

## 📁 Repository Structure

/
├── static/                 # Public site root (served by Netlify)
│   ├── index.html          # Homepage
│   ├── robots.txt          # SEO crawl rules
│   ├── sitemap.xml         # Sitemap for search engines
│   ├── _headers            # Netlify headers (ownership + attribution)
│   ├── attribution.html    # Reusable attribution block
│   ├── assets/             # Images, logos, media
│   ├── blog/               # Blog posts
│   ├── case-studies/       # Case studies
│   ├── faqs/               # FAQs
│   ├── resources/          # Resources
│   ├── css/                # Stylesheets
│   └── js/                 # Attribution scripts
│
├── utilities/              # Internal tools (not served publicly)
│   └── posts-generator.html
│
└── README.md               # Documentation

---

## 🚀 Deployment

Netlify automatically deploys the contents of `/static/` as the site root.

Example:
- `/static/index.html` → https://yourdomain.com/
- `/static/blog/` → https://yourdomain.com/blog/

---

## 🧩 SEO Files

- `robots.txt` and `sitemap.xml` must remain inside `/static/`
- Netlify serves them at the site root automatically

---

## 🛠 Internal Tools

The `/utilities/` folder contains internal tools such as:
- `posts-generator.html` — JSON generator for posts.json

These files are **not** deployed and should remain at the repo root.

---

## 🧹 Cleanup Notes

The following files should never exist at the repo root:
- `/index.html`
- `/_redirects`
- `/netlify.toml`
- `/robots.txt`
- `/sitemap.xml`

All public content must live inside `/static/`.

---

## ✔ Status

This repository is now aligned with:
- SLP CONNECT™ architecture  
- Netlify static hosting  
- SEO best practices  
- Attribution and ownership requirements  
