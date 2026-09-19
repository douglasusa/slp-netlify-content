# SLP CONNECT™ Content Hub  
Static content repository for Netlify deployment

This repository contains the complete static version of the SLP CONNECT™ Content Hub.  
All public-facing content is served directly from the `/static/` directory.

---

## 📁 Repository Structure

/
├── netlify.toml            # Build + publish configuration (source of truth)
├── static/                 # Public site root (served by Netlify)
│   ├── index.html          # Homepage
│   ├── compliance.html     # Compliance page
│   ├── landing-page.html   # Landing page
│   ├── hero-section.html   # Reusable hero markup
│   ├── navigation-index.html # Reusable navigation markup
│   ├── robots.txt          # SEO crawl rules
│   ├── sitemap-index.xml   # Sitemap index
│   ├── sitemap-*.xml       # Per-section sitemaps (blog, faqs, news, …)
│   ├── _redirects          # Redirect + URL canonicalization rules
│   ├── assets/             # Static assets
│   │   ├── css/            # Stylesheets
│   │   ├── images/         # Images and media
│   │   └── logos/          # Logo and wordmark files
│   ├── blog/               # Blog posts
│   ├── case-studies/       # Case studies
│   ├── faqs/               # FAQs
│   ├── news/               # News items
│   ├── resources/          # Resources
│   └── testimonials/       # Testimonials
│
├── scripts/                # Maintenance scripts invoked by GitHub Actions
├── utilities/              # Internal tools (not served publicly)
│   └── posts-generator.html
│
├── .github/workflows/      # Content automation workflows
├── google0fb19b8638c06533.html  # Search Console verification
└── README.md               # Documentation

---

## 🚀 Deployment

Netlify automatically deploys the contents of `/static/` as the site root.

Example:
- `/static/index.html` → https://yourdomain.com/
- `/static/blog/` → https://yourdomain.com/blog/

---

## 🔧 Build Configuration

There is no build step. The site is hand-authored static HTML, and `netlify.toml`
at the repo root declares the publish directory and an explicit no-op build command.

Keep build settings in `netlify.toml` rather than in the Netlify UI. Settings that
live only in the UI are unversioned, cannot be reviewed as part of a pull request,
and can be given different values per deploy context without leaving any trace in
the repository — which is how a deploy preview can fail on exactly the content that
then deploys cleanly to production.

The explicit build command matters: when no command is configured, Netlify falls
back to framework auto-detection and may supply one of its own.

---

## 🧩 SEO Files

- `robots.txt` and the `sitemap-*.xml` files must remain inside `/static/`
- Netlify serves them at the site root automatically
- `_redirects` carries the redirect and canonicalization rules; see the comments
  in that file before adding trailing-slash rules

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
- `/robots.txt`
- `/sitemap.xml`

All public content must live inside `/static/`.

`netlify.toml` is the one exception and belongs at the repo root: it is build
configuration, is never served to visitors, and Netlify only reads it from there.

---

## ✔ Status

This repository is now aligned with:
- SLP CONNECT™ architecture  
- Netlify static hosting  
- SEO best practices  
- Attribution and ownership requirements  
