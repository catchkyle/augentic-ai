#!/usr/bin/env python3
"""Build script for Augentic AI site - blogs, booking, lead magnet."""

import markdown
import frontmatter

NAV = """<nav id="nav">
  <div class="container">
    <a href="/" class="nav-logo" style="display:flex;align-items:center;gap:0;text-decoration:none;">
      <svg width="160" height="37" viewBox="0 0 1400 320" xmlns="http://www.w3.org/2000/svg" style="overflow:visible;">
        <g transform="translate(70,20)">
          <path fill="#D4AF37" fill-rule="evenodd" d="M130 0 L20 280 H80 L130 155 L180 280 H240 L130 0 Z M130 78 L96 170 H164 L130 78 Z"/>
        </g>
        <g transform="translate(360,0)">
          <text x="0" y="200" fill="#D4AF37" font-family="Inter,system-ui,sans-serif" font-size="92" font-weight="700" letter-spacing="6">AUGENTIC</text>
          <text x="835" y="200" fill="#D4AF37" font-family="Inter,system-ui,sans-serif" font-size="92" font-weight="500" letter-spacing="6"> AI</text>
        </g>
      </svg>
    </a>
    <ul class="nav-links">
      <li><a href="/#solution">Solutions</a></li>
      <li><a href="/#offerings">Offerings</a></li>
      <li><a href="/blog/">Insights</a></li>
      <li><a href="/guide/">AI Guide</a></li>
    </ul>
    <a href="/book/" class="nav-cta">Book Strategy Call</a>
    <button class="theme-toggle" id="themeToggle" aria-label="Toggle theme">
      <svg id="iconSun" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="display:none"><circle cx="12" cy="12" r="5"/><line x1="12" y1="2" x2="12" y2="4"/><line x1="12" y1="20" x2="12" y2="22"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="2" y1="12" x2="4" y2="12"/><line x1="20" y1="12" x2="22" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
      <svg id="iconMoon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
    </button>
    <button class="hamburger" id="hamburger" aria-label="Menu"><span></span><span></span><span></span></button>
  </div>
</nav>
<div class="mobile-menu" id="mobileMenu">
  <a href="/#solution" onclick="closeMobile()">Solutions</a>
  <a href="/#offerings" onclick="closeMobile()">Offerings</a>
  <a href="/blog/" onclick="closeMobile()">Insights</a>
  <a href="/guide/" onclick="closeMobile()">AI Guide</a>
  <a href="/book/" onclick="closeMobile()" style="color:var(--accent);">Book Strategy Call</a>
</div>"""

FOOTER = """<footer>
  <div class="container">
    <div class="footer-inner">
      <div>
        <div class="footer-logo" style="display:flex;align-items:center;">
          <svg width="120" height="28" viewBox="0 0 1400 320" xmlns="http://www.w3.org/2000/svg">
            <g transform="translate(70,20)"><path fill="#D4AF37" fill-rule="evenodd" d="M130 0 L20 280 H80 L130 155 L180 280 H240 L130 0 Z M130 78 L96 170 H164 L130 78 Z"/></g>
            <g transform="translate(360,0)">
              <text x="0" y="200" fill="#D4AF37" font-family="Inter,system-ui,sans-serif" font-size="92" font-weight="700" letter-spacing="6">AUGENTIC</text>
              <text x="835" y="200" fill="#D4AF37" font-family="Inter,system-ui,sans-serif" font-size="92" font-weight="500" letter-spacing="6"> AI</text>
            </g>
          </svg>
        </div>
        <div class="footer-tagline">Autonomous AI. Measurable Revenue.</div>
      </div>
      <ul class="footer-links">
        <li><a href="/#solution">Solutions</a></li>
        <li><a href="/#offerings">Offerings</a></li>
        <li><a href="/blog/">Insights</a></li>
        <li><a href="/guide/">AI Guide</a></li>
        <li><a href="/book/">Book a Call</a></li>
        <li><a href="mailto:hello@augenticai.com">Contact</a></li>
      </ul>
      <div class="footer-copy">&copy; 2026 Augentic AI. All rights reserved.</div>
    </div>
  </div>
</footer>"""

BASE_CSS = """<link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:wght@400;500;600&display=swap" rel="stylesheet" />
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' fill='%230B0B0B'/%3E%3Cpath fill='%23D4AF37' fill-rule='evenodd' d='M50 5 L5 95 H25 L50 57 L75 95 H95 L50 5 Z M50 30 L35 68 H65 L50 30 Z'/%3E%3C/svg%3E" />
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --bg: #0A0A0A; --bg-card: #111111; --bg-raised: #161616;
      --text: #F5F5F0; --text-muted: #888880; --text-dim: #555550;
      --accent: #D4AF37; --accent-dim: rgba(212,175,55,0.12);
      --border: rgba(255,255,255,0.07); --border-accent: rgba(212,175,55,0.3);
      --font-serif: 'Playfair Display', Georgia, serif;
      --font-sans: 'Inter', system-ui, sans-serif;
      --max: 1200px; --radius: 2px;
    }
    body.light {
      --bg: #FAFAF7; --bg-card: #F2F2EE; --bg-raised: #E8E8E4;
      --text: #0B0B0B; --text-muted: #444440; --text-dim: #999990;
      --border: rgba(0,0,0,0.08); --border-accent: rgba(212,175,55,0.4);
    }
    html { scroll-behavior: smooth; }
    body { background: var(--bg); color: var(--text); font-family: var(--font-sans); font-weight: 300; line-height: 1.7; -webkit-font-smoothing: antialiased; }
    ::selection { background: var(--accent-dim); color: var(--accent); }
    h1,h2,h3,h4 { font-weight: 400; line-height: 1.25; letter-spacing: -0.02em; }
    h1 { font-family: var(--font-serif); font-size: clamp(2rem,4vw,3.2rem); }
    h2 { font-family: var(--font-serif); font-size: clamp(1.6rem,3vw,2.4rem); }
    h3 { font-family: var(--font-sans); font-size: 1.05rem; font-weight: 500; letter-spacing: 0; }
    p { color: var(--text-muted); line-height: 1.85; }
    a { color: inherit; }
    .label { font-size: 0.7rem; font-weight: 600; letter-spacing: 0.2em; text-transform: uppercase; color: var(--accent); }
    .container { max-width: var(--max); margin: 0 auto; padding: 0 2rem; }
    nav { position: fixed; top: 0; left: 0; right: 0; z-index: 100; padding: 1.5rem 0; transition: background 0.4s, padding 0.3s; }
    nav.scrolled { background: rgba(10,10,10,0.95); border-bottom: 1px solid var(--border); padding: 1rem 0; backdrop-filter: blur(12px); }
    body.light nav.scrolled { background: rgba(250,250,247,0.95); }
    nav .container { display: flex; align-items: center; justify-content: space-between; gap: 1.5rem; }
    .nav-links { display: flex; align-items: center; gap: 2rem; list-style: none; }
    .nav-links a { font-size: 0.8rem; color: var(--text-muted); text-decoration: none; transition: color 0.2s; }
    .nav-links a:hover { color: var(--text); }
    .nav-cta { font-size: 0.78rem; font-weight: 500; letter-spacing: 0.08em; padding: 0.65rem 1.4rem; background: var(--accent); color: #0A0A0A; text-decoration: none; border-radius: var(--radius); transition: opacity 0.2s; white-space: nowrap; }
    .nav-cta:hover { opacity: 0.88; }
    .theme-toggle { background: none; border: 1px solid var(--border); color: var(--text-muted); cursor: pointer; width: 34px; height: 34px; display: flex; align-items: center; justify-content: center; border-radius: var(--radius); transition: color 0.2s; flex-shrink: 0; }
    .theme-toggle:hover { color: var(--accent); }
    .hamburger { display: none; flex-direction: column; gap: 5px; cursor: pointer; background: none; border: none; padding: 4px; }
    .hamburger span { display: block; width: 22px; height: 1px; background: var(--text); }
    .mobile-menu { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 99; background: var(--bg); padding: 6rem 2rem 2rem; flex-direction: column; gap: 2rem; }
    .mobile-menu.open { display: flex; }
    .mobile-menu a { font-size: 1.4rem; color: var(--text); text-decoration: none; border-bottom: 1px solid var(--border); padding-bottom: 1.2rem; }
    footer { background: var(--bg); border-top: 1px solid var(--border); padding: 3rem 0; }
    .footer-inner { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1.5rem; }
    .footer-tagline { font-size: 0.78rem; color: var(--text-dim); margin-top: 0.3rem; }
    .footer-links { display: flex; gap: 2rem; list-style: none; flex-wrap: wrap; }
    .footer-links a { font-size: 0.78rem; color: var(--text-dim); text-decoration: none; transition: color 0.2s; }
    .footer-links a:hover { color: var(--text-muted); }
    .footer-copy { font-size: 0.75rem; color: var(--text-dim); }
    .divider { height: 1px; background: linear-gradient(90deg, transparent, var(--border), transparent); }
    .btn-primary { display: inline-block; padding: 0.9rem 2rem; background: var(--accent); color: #0A0A0A; font-size: 0.82rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; text-decoration: none; border-radius: var(--radius); transition: opacity 0.2s, transform 0.2s; border: none; cursor: pointer; }
    .btn-primary:hover { opacity: 0.88; transform: translateY(-1px); }
    .btn-outline { display: inline-block; padding: 0.85rem 1.8rem; border: 1px solid var(--border-accent); color: var(--accent); font-size: 0.82rem; font-weight: 500; letter-spacing: 0.08em; text-decoration: none; border-radius: var(--radius); transition: all 0.2s; }
    .btn-outline:hover { background: var(--accent-dim); }
    @media (max-width: 900px) { .nav-links, .nav-cta { display: none; } .hamburger { display: flex; } }
  </style>"""

BASE_JS = """<script>
  const nav = document.getElementById('nav');
  window.addEventListener('scroll', () => { nav.classList.toggle('scrolled', window.scrollY > 40); }, { passive: true });
  const hamburger = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobileMenu');
  hamburger.addEventListener('click', () => { mobileMenu.classList.toggle('open'); });
  function closeMobile() { mobileMenu.classList.remove('open'); }
  const themeToggle = document.getElementById('themeToggle');
  const iconSun = document.getElementById('iconSun');
  const iconMoon = document.getElementById('iconMoon');
  const savedTheme = localStorage.getItem('theme') || 'dark';
  if (savedTheme === 'light') { document.body.classList.add('light'); iconSun.style.display = 'block'; iconMoon.style.display = 'none'; }
  themeToggle.addEventListener('click', () => {
    const isLight = document.body.classList.toggle('light');
    localStorage.setItem('theme', isLight ? 'light' : 'dark');
    iconSun.style.display = isLight ? 'block' : 'none';
    iconMoon.style.display = isLight ? 'none' : 'block';
  });
</script>"""

# ───────────────────────────────────────────────────────────────
# BLOG POSTS
# ───────────────────────────────────────────────────────────────

def load_blog_posts_from_markdown():
    """Load blog posts from content/blog/*.md files with frontmatter."""
    import os
    import glob

    posts = []
    content_dir = "content/blog"

    if not os.path.exists(content_dir):
        print(f"ERROR: {content_dir} directory not found")
        return None

    md_files = glob.glob(os.path.join(content_dir, "*.md"))

    if not md_files:
        print(f"ERROR: No markdown files found in {content_dir}")
        return None

    md = markdown.Markdown(extensions=['extra', 'codehilite', 'fenced_code'])

    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)

                # Convert markdown body to HTML
                body_html = md.convert(post.content)
                md.reset()  # Reset for next file

                # Build post dict from frontmatter + body
                post_data = {
                    "slug": post.get('slug', os.path.splitext(os.path.basename(md_file))[0]),
                    "title": post.get('title', 'Untitled'),
                    "date": post.get('date', ''),
                    "category": post.get('category', 'Uncategorized'),
                    "description": post.get('description', ''),
                    "reading_time": post.get('reading_time', ''),
                    "featured": post.get('featured', False),
                    "x_credit": post.get('x_credit', ''),
                    "body": body_html
                }
                posts.append(post_data)
        except Exception as e:
            print(f"Error loading {md_file}: {e}")
            continue

    # Sort by date (newest first)
    posts.sort(key=lambda p: p.get('date', ''), reverse=True)

    print(f"Blog posts: {len(posts)} loaded from markdown")
    return posts


def load_case_studies_from_markdown():
    """Load case studies from content/case-studies/*.md files with frontmatter."""
    import os
    import glob

    studies = []
    content_dir = "content/case-studies"

    if not os.path.exists(content_dir):
        print(f"Warning: {content_dir} not found, no case studies to load")
        return []

    md_files = glob.glob(os.path.join(content_dir, "*.md"))

    if not md_files:
        print(f"Warning: No markdown files found in {content_dir}, no case studies to load")
        return []

    md = markdown.Markdown(extensions=['extra', 'codehilite', 'fenced_code'])

    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                study = frontmatter.load(f)

                # Convert markdown body to HTML
                body_html = md.convert(study.content)
                md.reset()  # Reset for next file

                # Build study dict from frontmatter + body
                study_data = {
                    "slug": study.get('slug', os.path.splitext(os.path.basename(md_file))[0]),
                    "title": study.get('title', 'Untitled'),
                    "client": study.get('client', ''),
                    "industry": study.get('industry', ''),
                    "date": study.get('date', ''),
                    "challenge": study.get('challenge', ''),
                    "solution": study.get('solution', ''),
                    "results": study.get('results', ''),
                    "featured": study.get('featured', False),
                    "body": body_html
                }
                studies.append(study_data)

        except Exception as e:
            print(f"Error loading {md_file}: {e}")
            continue

    # Sort by date (newest first)
    studies.sort(key=lambda s: s.get('date', ''), reverse=True)

    print(f"Case studies: {len(studies)} loaded from markdown")
    return studies


# Load posts from markdown files
POSTS = load_blog_posts_from_markdown()
if POSTS is None:
    print("ERROR: Failed to load blog posts from content/blog/")
    print("Ensure content/blog/ directory exists and contains .md files")
    exit(1)

# Load case studies from markdown files
CASE_STUDIES = load_case_studies_from_markdown()

def make_blog_post(post):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{post['title']} | Augentic AI Insights</title>
  <meta name="description" content="{post['description']}" />
  <meta property="og:title" content="{post['title']}" />
  <meta property="og:description" content="{post['description']}" />
  <meta property="og:type" content="article" />
  {BASE_CSS}
  <style>
    .post-header {{ padding: 10rem 0 4rem; border-bottom: 1px solid var(--border); }}
    .post-meta {{ display: flex; align-items: center; gap: 1.5rem; margin-bottom: 2rem; flex-wrap: wrap; }}
    .post-meta .label {{ margin: 0; }}
    .post-meta-text {{ font-size: 0.8rem; color: var(--text-dim); }}
    .post-title {{ margin-bottom: 1.2rem; }}
    .post-desc {{ font-size: 1.05rem; max-width: 640px; }}
    .post-body {{ padding: 5rem 0; }}
    .post-body-inner {{ max-width: 720px; }}
    .post-body p {{ margin-bottom: 1.6rem; font-size: 1rem; }}
    .post-body h2 {{ font-size: 1.5rem; margin: 3rem 0 1rem; color: var(--text); }}
    .post-body strong {{ color: var(--text); font-weight: 500; }}
    .x-credit {{ background: var(--bg-card); border: 1px solid var(--border-accent); border-left: 3px solid var(--accent); padding: 1.2rem 1.5rem; margin: 2.5rem 0; font-size: 0.88rem; color: var(--text-muted); font-style: italic; border-radius: 0 var(--radius) var(--radius) 0; }}
    .post-footer {{ padding: 4rem 0; border-top: 1px solid var(--border); }}
    .cta-box {{ background: var(--bg-card); border: 1px solid var(--border); padding: 3rem; text-align: center; max-width: 600px; margin: 0 auto; }}
    .cta-box h3 {{ font-family: var(--font-serif); font-size: 1.6rem; margin-bottom: 1rem; color: var(--text); }}
    .cta-box p {{ margin-bottom: 2rem; }}
    .back-link {{ display: inline-flex; align-items: center; gap: 0.5rem; font-size: 0.82rem; color: var(--text-muted); text-decoration: none; margin-bottom: 3rem; transition: color 0.2s; }}
    .back-link:hover {{ color: var(--accent); }}
  </style>
</head>
<body>
{NAV}

<div class="post-header">
  <div class="container">
    <a href="/blog/" class="back-link">
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M13 7H1M6 2L1 7l5 5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
      Back to Insights
    </a>
    <div class="post-meta">
      <span class="label">{post['category']}</span>
      <span class="post-meta-text">{post['date']}</span>
      <span class="post-meta-text">{post['reading_time']}</span>
    </div>
    <h1 class="post-title">{post['title']}</h1>
    <p class="post-desc">{post['description']}</p>
  </div>
</div>

<div class="post-body">
  <div class="container">
    <div class="post-body-inner">
      {f'<div class="x-credit">{post["x_credit"]}</div>' if post.get('x_credit') else ''}
      {post['body']}
    </div>
  </div>
</div>

<div class="post-footer">
  <div class="container">
    <div class="cta-box">
      <h3>Ready to Build Your AI Workforce?</h3>
      <p>Schedule a 30-minute strategy call. We will tell you exactly what we would build for your business - and what it would cost.</p>
      <a href="/book/" class="btn-primary">Book a Strategy Call</a>
    </div>
  </div>
</div>

{FOOTER}
{BASE_JS}
</body>
</html>"""


def make_blog_index():
    cards = ""
    for p in POSTS:
        featured_class = ' style="border-color:var(--border-accent);"' if p.get('featured') else ''
        cards += f"""
      <article class="blog-card"{featured_class}>
        <a href="/blog/{p['slug']}/" class="blog-card-link">
          <div class="blog-card-meta">
            <span class="label" style="font-size:0.65rem;">{p['category']}</span>
            <span class="blog-date">{p['date']}</span>
          </div>
          <h3 class="blog-card-title">{p['title']}</h3>
          <p class="blog-card-desc">{p['description']}</p>
          <div class="blog-card-footer">
            <span class="blog-read">{p['reading_time']}</span>
            <span class="blog-arrow">Read &rarr;</span>
          </div>
        </a>
      </article>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Insights | Augentic AI - AI Systems Integration</title>
  <meta name="description" content="Analysis, frameworks, and perspectives on autonomous AI systems for revenue-driven businesses." />
  {BASE_CSS}
  <style>
    .blog-header {{ padding: 10rem 0 5rem; border-bottom: 1px solid var(--border); }}
    .blog-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1px; background: var(--border); margin-top: 5rem; }}
    .blog-card {{ background: var(--bg); transition: background 0.2s; border: 1px solid transparent; }}
    .blog-card:hover {{ background: var(--bg-card); }}
    .blog-card-link {{ display: block; padding: 2.5rem; text-decoration: none; color: inherit; height: 100%; }}
    .blog-card-meta {{ display: flex; align-items: center; gap: 1rem; margin-bottom: 1.2rem; flex-wrap: wrap; }}
    .blog-date {{ font-size: 0.72rem; color: var(--text-dim); }}
    .blog-card-title {{ font-size: 1.05rem; font-weight: 500; color: var(--text); margin-bottom: 0.8rem; line-height: 1.4; letter-spacing: -0.01em; }}
    .blog-card-desc {{ font-size: 0.88rem; line-height: 1.75; margin-bottom: 2rem; }}
    .blog-card-footer {{ display: flex; justify-content: space-between; align-items: center; }}
    .blog-read {{ font-size: 0.75rem; color: var(--text-dim); }}
    .blog-arrow {{ font-size: 0.8rem; color: var(--accent); }}
    @media (max-width: 900px) {{ .blog-grid {{ grid-template-columns: 1fr 1fr; }} }}
    @media (max-width: 600px) {{ .blog-grid {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
{NAV}

<div class="blog-header">
  <div class="container">
    <span class="label">Insights</span>
    <h1 style="margin-top:1rem;margin-bottom:1rem;">Perspectives on Autonomous AI</h1>
    <p style="max-width:560px;font-size:1.05rem;">Analysis, frameworks, and perspectives on AI systems integration for revenue-driven businesses. No hype. No fluff. Just substance.</p>
  </div>
</div>

<div style="padding:0 0 8rem;">
  <div class="container">
    <div class="blog-grid">{cards}
    </div>
  </div>
</div>

{FOOTER}
{BASE_JS}
</body>
</html>"""


# ───────────────────────────────────────────────────────────────
# CASE STUDIES
# ───────────────────────────────────────────────────────────────

def make_case_study(study):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{study['title']} | Augentic AI Case Studies</title>
  <meta name="description" content="{study['challenge']}" />
  <meta property="og:title" content="{study['title']}" />
  <meta property="og:description" content="{study['challenge']}" />
  <meta property="og:type" content="article" />
  {BASE_CSS}
  <style>
    .case-header {{ padding: 10rem 0 4rem; border-bottom: 1px solid var(--border); }}
    .case-meta {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 2rem; margin-bottom: 3rem; }}
    .case-meta-item {{ }}
    .case-meta-label {{ font-size: 0.7rem; font-weight: 600; letter-spacing: 0.2em; text-transform: uppercase; color: var(--accent); margin-bottom: 0.5rem; }}
    .case-meta-value {{ font-size: 0.9rem; color: var(--text-muted); }}
    .case-title {{ margin-bottom: 1.2rem; }}
    .case-body {{ padding: 5rem 0; }}
    .case-body-inner {{ max-width: 720px; }}
    .case-body p {{ margin-bottom: 1.6rem; font-size: 1rem; }}
    .case-body h2 {{ font-size: 1.5rem; margin: 3rem 0 1rem; color: var(--text); }}
    .case-body strong {{ color: var(--text); font-weight: 500; }}
    .case-highlights {{ background: var(--bg-card); border: 1px solid var(--border); padding: 2.5rem; margin: 3rem 0; }}
    .case-highlights h3 {{ font-size: 1.1rem; margin-bottom: 1.5rem; color: var(--text); }}
    .case-highlight-grid {{ display: grid; gap: 1.5rem; }}
    .case-highlight-item {{ }}
    .case-highlight-label {{ font-size: 0.7rem; font-weight: 600; letter-spacing: 0.15em; text-transform: uppercase; color: var(--accent); margin-bottom: 0.5rem; }}
    .case-highlight-value {{ font-size: 0.95rem; color: var(--text-muted); line-height: 1.6; }}
    .case-footer {{ padding: 4rem 0; border-top: 1px solid var(--border); }}
    .cta-box {{ background: var(--bg-card); border: 1px solid var(--border); padding: 3rem; text-align: center; max-width: 600px; margin: 0 auto; }}
    .cta-box h3 {{ font-family: var(--font-serif); font-size: 1.6rem; margin-bottom: 1rem; color: var(--text); }}
    .cta-box p {{ margin-bottom: 2rem; }}
    .back-link {{ display: inline-flex; align-items: center; gap: 0.5rem; font-size: 0.82rem; color: var(--text-muted); text-decoration: none; margin-bottom: 3rem; transition: color 0.2s; }}
    .back-link:hover {{ color: var(--accent); }}
  </style>
</head>
<body>
{NAV}

<div class="case-header">
  <div class="container">
    <a href="/case-studies/" class="back-link">
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M13 7H1M6 2L1 7l5 5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
      Back to Case Studies
    </a>
    <div class="case-meta">
      <div class="case-meta-item">
        <div class="case-meta-label">Client</div>
        <div class="case-meta-value">{study['client']}</div>
      </div>
      <div class="case-meta-item">
        <div class="case-meta-label">Industry</div>
        <div class="case-meta-value">{study['industry']}</div>
      </div>
    </div>
    <h1 class="case-title">{study['title']}</h1>
  </div>
</div>

<div class="case-body">
  <div class="container">
    <div class="case-body-inner">
      <div class="case-highlights">
        <h3>Project Overview</h3>
        <div class="case-highlight-grid">
          <div class="case-highlight-item">
            <div class="case-highlight-label">Challenge</div>
            <div class="case-highlight-value">{study['challenge']}</div>
          </div>
          <div class="case-highlight-item">
            <div class="case-highlight-label">Solution</div>
            <div class="case-highlight-value">{study['solution']}</div>
          </div>
          <div class="case-highlight-item">
            <div class="case-highlight-label">Results</div>
            <div class="case-highlight-value">{study['results']}</div>
          </div>
        </div>
      </div>
      {study['body']}
    </div>
  </div>
</div>

<div class="case-footer">
  <div class="container">
    <div class="cta-box">
      <h3>Ready to Build Your AI Workforce?</h3>
      <p>Schedule a 30-minute strategy call. We will tell you exactly what we would build for your business - and what it would cost.</p>
      <a href="/book/" class="btn-primary">Book a Strategy Call</a>
    </div>
  </div>
</div>

{FOOTER}
{BASE_JS}
</body>
</html>"""


def make_case_studies_index():
    cards = ""
    for study in CASE_STUDIES:
        featured_class = ' style="border-color:var(--border-accent);"' if study.get('featured') else ''
        cards += f"""
      <article class="case-card"{featured_class}>
        <a href="/case-studies/{study['slug']}/" class="case-card-link">
          <div class="case-card-meta">
            <span class="label" style="font-size:0.65rem;">{study['industry']}</span>
            <span class="case-date">{study['date']}</span>
          </div>
          <h3 class="case-card-title">{study['title']}</h3>
          <div class="case-card-client">{study['client']}</div>
          <p class="case-card-results">{study['results']}</p>
          <div class="case-card-footer">
            <span class="case-arrow">View Case Study &rarr;</span>
          </div>
        </a>
      </article>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Case Studies | Augentic AI - AI Systems Integration</title>
  <meta name="description" content="Real-world AI systems integration projects delivering measurable business outcomes." />
  {BASE_CSS}
  <style>
    .case-studies-header {{ padding: 10rem 0 5rem; border-bottom: 1px solid var(--border); }}
    .case-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1px; background: var(--border); margin-top: 5rem; }}
    .case-card {{ background: var(--bg); transition: background 0.2s; border: 1px solid transparent; }}
    .case-card:hover {{ background: var(--bg-card); }}
    .case-card-link {{ display: block; padding: 2.5rem; text-decoration: none; color: inherit; height: 100%; }}
    .case-card-meta {{ display: flex; align-items: center; gap: 1rem; margin-bottom: 1.2rem; flex-wrap: wrap; }}
    .case-date {{ font-size: 0.72rem; color: var(--text-dim); }}
    .case-card-title {{ font-size: 1.05rem; font-weight: 500; color: var(--text); margin-bottom: 0.5rem; line-height: 1.4; letter-spacing: -0.01em; }}
    .case-card-client {{ font-size: 0.8rem; color: var(--text-dim); margin-bottom: 1rem; }}
    .case-card-results {{ font-size: 0.88rem; line-height: 1.75; margin-bottom: 2rem; }}
    .case-card-footer {{ display: flex; justify-content: flex-end; align-items: center; }}
    .case-arrow {{ font-size: 0.8rem; color: var(--accent); }}
    @media (max-width: 900px) {{ .case-grid {{ grid-template-columns: 1fr 1fr; }} }}
    @media (max-width: 600px) {{ .case-grid {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
{NAV}

<div class="case-studies-header">
  <div class="container">
    <span class="label">Case Studies</span>
    <h1 style="margin-top:1rem;margin-bottom:1rem;">AI Systems That Deliver</h1>
    <p style="max-width:560px;font-size:1.05rem;">Real-world AI systems integration projects delivering measurable business outcomes for revenue-driven companies.</p>
  </div>
</div>

<div style="padding:0 0 8rem;">
  <div class="container">
    <div class="case-grid">{cards}
    </div>
  </div>
</div>

{FOOTER}
{BASE_JS}
</body>
</html>"""


def make_booking_page():
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Book a Strategy Call | Augentic AI</title>
  <meta name="description" content="Schedule a 30-minute strategy call with Augentic AI. We will assess your workflows and identify your highest-leverage automation opportunities." />
  {BASE_CSS}
  <style>
    .book-layout {{ min-height: 100vh; display: grid; grid-template-columns: 1fr 1fr; }}
    .book-left {{ padding: 10rem 5rem 5rem; background: var(--bg-card); border-right: 1px solid var(--border); display: flex; flex-direction: column; justify-content: center; }}
    .book-right {{ padding: 10rem 5rem 5rem; display: flex; flex-direction: column; justify-content: center; }}
    .book-left h1 {{ margin: 1rem 0 1.2rem; }}
    .book-left p {{ margin-bottom: 3rem; font-size: 1.05rem; }}
    .what-to-expect {{ list-style: none; }}
    .what-to-expect li {{ display: flex; gap: 1rem; padding: 1rem 0; border-bottom: 1px solid var(--border); font-size: 0.9rem; color: var(--text-muted); align-items: flex-start; }}
    .what-to-expect li:last-child {{ border-bottom: none; }}
    .expect-icon {{ color: var(--accent); flex-shrink: 0; margin-top: 0.1rem; font-style: normal; }}
    .form-group {{ display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 1rem; }}
    .form-group label {{ font-size: 0.72rem; font-weight: 500; letter-spacing: 0.12em; text-transform: uppercase; color: var(--text-muted); }}
    .form-group input, .form-group select, .form-group textarea {{
      background: var(--bg-card); border: 1px solid var(--border); color: var(--text);
      font-family: var(--font-sans); font-size: 0.9rem; padding: 0.85rem 1rem;
      border-radius: var(--radius); transition: border-color 0.2s; width: 100%; outline: none; appearance: none;
    }}
    .form-group input:focus, .form-group select:focus, .form-group textarea:focus {{ border-color: var(--accent); }}
    .form-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }}
    .form-group select {{ background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23888880' d='M6 8L1 3h10z'/%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 1rem center; padding-right: 2.5rem; cursor: pointer; }}
    .form-note {{ font-size: 0.78rem; color: var(--text-dim); margin-top: 1rem; }}
    @media (max-width: 900px) {{ .book-layout {{ grid-template-columns: 1fr; }} .book-left {{ padding: 8rem 2rem 3rem; }} .book-right {{ padding: 3rem 2rem 5rem; }} .form-row {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
{NAV}

<div class="book-layout">
  <div class="book-left">
    <span class="label">Strategy Call</span>
    <h1>30 Minutes.<br>Clear Direction.</h1>
    <p>We assess your current workflow, identify your highest-value automation opportunities, and tell you exactly what we would build - and what it would cost. No sales pressure. No obligation.</p>
    <ul class="what-to-expect">
      <li><span class="expect-icon">&#10003;</span> Workflow audit - we map where your team is spending time on tasks AI should own</li>
      <li><span class="expect-icon">&#10003;</span> Opportunity identification - the three highest-ROI automation candidates in your business</li>
      <li><span class="expect-icon">&#10003;</span> System design overview - what an AI workforce would look like for your specific revenue model</li>
      <li><span class="expect-icon">&#10003;</span> Investment and timeline - honest numbers on what it costs and how long it takes</li>
      <li><span class="expect-icon">&#10003;</span> Fit assessment - we will tell you if we are not the right partner for your situation</li>
    </ul>
  </div>
  <div class="book-right">
    <h2 style="margin-bottom:0.5rem;">Request Your Strategy Call</h2>
    <p style="margin-bottom:2rem;font-size:0.9rem;">We respond within one business day to schedule your call.</p>
    <form onsubmit="handleBook(event)">
      <div class="form-row">
        <div class="form-group">
          <label>First Name</label>
          <input type="text" name="firstName" placeholder="John" required />
        </div>
        <div class="form-group">
          <label>Last Name</label>
          <input type="text" name="lastName" placeholder="Smith" required />
        </div>
      </div>
      <div class="form-group">
        <label>Work Email</label>
        <input type="email" name="email" placeholder="john@company.com" required />
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>Company</label>
          <input type="text" name="company" placeholder="Acme Corp" required />
        </div>
        <div class="form-group">
          <label>Your Role</label>
          <select name="role" required>
            <option value="" disabled selected>Select role</option>
            <option>Founder / CEO</option>
            <option>CIO / CTO</option>
            <option>VP / Director of Sales</option>
            <option>VP / Director of Revenue Ops</option>
            <option>Other Executive</option>
          </select>
        </div>
      </div>
      <div class="form-group">
        <label>Annual Revenue</label>
        <select name="revenue" required>
          <option value="" disabled selected>Select revenue range</option>
          <option>$5M - $10M</option>
          <option>$10M - $25M</option>
          <option>$25M - $50M</option>
          <option>$50M - $100M</option>
          <option>$100M+</option>
        </select>
      </div>
      <div class="form-group">
        <label>Primary AI Interest</label>
        <select name="interest" required>
          <option value="" disabled selected>What are you most interested in?</option>
          <option>Autonomous AI Agents for Sales and Revenue</option>
          <option>AI Integration into CRM and Sales Workflows</option>
          <option>AI-Driven Email and Outreach Automation</option>
          <option>AI Voice Agents for Front Office</option>
          <option>Full AI Workforce Automation</option>
          <option>Automated Reporting and Business Intelligence</option>
          <option>AI Scheduling and Calendar Automation</option>
          <option>Not Sure - Need a Strategy Assessment</option>
        </select>
      </div>
      <button type="submit" class="btn-primary" style="width:100%;margin-top:0.5rem;font-size:0.85rem;padding:1rem;">Request Strategy Call</button>
      <p class="form-note">We respond within one business day. No spam. No sales scripts.</p>
    </form>
  </div>
</div>

{FOOTER}
{BASE_JS}
<script>
function handleBook(e) {{
  e.preventDefault();
  const btn = e.target.querySelector('button[type="submit"]');
  const data = Object.fromEntries(new FormData(e.target));
  btn.textContent = 'Sending...'; btn.disabled = true;
  const subject = encodeURIComponent('Strategy Call Request - ' + data.company);
  const body = encodeURIComponent('Name: ' + data.firstName + ' ' + data.lastName + '\\nEmail: ' + data.email + '\\nCompany: ' + data.company + '\\nRole: ' + data.role + '\\nRevenue: ' + data.revenue + '\\nInterest: ' + data.interest);
  setTimeout(() => {{
    btn.textContent = 'Request Sent - We Will Be In Touch';
    btn.style.background = '#2a5a2a'; btn.style.color = '#90d090';
    window.location.href = 'mailto:hello@augenticai.com?subject=' + subject + '&body=' + body;
  }}, 600);
}}
</script>
</body>
</html>"""


def make_guide_page():
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AI Workforce Readiness Guide | Augentic AI</title>
  <meta name="description" content="The executive guide to evaluating your organization's readiness for autonomous AI workforce deployment. Free assessment framework inside." />
  {BASE_CSS}
  <style>
    .guide-hero {{ padding: 10rem 0 6rem; text-align: center; position: relative; overflow: hidden; }}
    .guide-hero::before {{ content: ''; position: absolute; inset: 0; background-image: linear-gradient(rgba(212,175,55,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(212,175,55,0.04) 1px, transparent 1px); background-size: 60px 60px; }}
    .guide-hero-inner {{ position: relative; z-index: 1; max-width: 680px; margin: 0 auto; }}
    .guide-hero h1 {{ margin: 1rem 0 1.2rem; }}
    .guide-hero p {{ font-size: 1.05rem; margin-bottom: 3rem; }}
    .guide-badge {{ display: inline-flex; align-items: center; gap: 0.5rem; background: var(--accent-dim); border: 1px solid var(--border-accent); padding: 0.4rem 1rem; border-radius: 999px; font-size: 0.75rem; color: var(--accent); font-weight: 500; letter-spacing: 0.05em; margin-bottom: 2rem; }}
    .guide-body {{ padding: 6rem 0; }}
    .guide-grid {{ display: grid; grid-template-columns: 1fr 1.4fr; gap: 6rem; align-items: start; }}
    .assessment-card {{ background: var(--bg-card); border: 1px solid var(--border); padding: 3rem; position: sticky; top: 100px; }}
    .assessment-card h3 {{ font-family: var(--font-serif); font-size: 1.5rem; color: var(--text); margin-bottom: 0.8rem; }}
    .assessment-card p {{ font-size: 0.9rem; margin-bottom: 2rem; }}
    .checklist-section {{ margin-bottom: 3rem; }}
    .checklist-section h4 {{ font-size: 0.72rem; font-weight: 600; letter-spacing: 0.15em; text-transform: uppercase; color: var(--accent); margin-bottom: 1.2rem; }}
    .checklist {{ list-style: none; }}
    .checklist li {{ display: flex; align-items: flex-start; gap: 1rem; padding: 0.6rem 0; border-bottom: 1px solid var(--border); font-size: 0.88rem; color: var(--text-muted); }}
    .checklist li:last-child {{ border-bottom: none; }}
    .check-box {{ width: 16px; height: 16px; border: 1px solid var(--border-accent); border-radius: 2px; flex-shrink: 0; margin-top: 0.1rem; cursor: pointer; transition: all 0.2s; }}
    .check-box.checked {{ background: var(--accent); border-color: var(--accent); }}
    .score-bar {{ margin-top: 2rem; padding-top: 2rem; border-top: 1px solid var(--border); }}
    .score-label {{ display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.8rem; }}
    .score-track {{ height: 4px; background: var(--border); border-radius: 2px; overflow: hidden; }}
    .score-fill {{ height: 100%; background: var(--accent); border-radius: 2px; transition: width 0.4s; width: 0%; }}
    .score-text {{ font-size: 0.82rem; color: var(--text-muted); margin-top: 0.8rem; }}
    .guide-content h2 {{ font-size: 1.8rem; margin: 3rem 0 1rem; }}
    .guide-content h2:first-child {{ margin-top: 0; }}
    .guide-content p {{ margin-bottom: 1.4rem; font-size: 0.97rem; }}
    .guide-content h3 {{ font-size: 1.05rem; font-weight: 500; color: var(--text); margin: 2rem 0 0.6rem; }}
    .stat-row {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1px; background: var(--border); margin: 2.5rem 0; }}
    .stat-box {{ background: var(--bg-card); padding: 2rem; text-align: center; }}
    .stat-num {{ font-family: var(--font-serif); font-size: 2.5rem; color: var(--accent); display: block; line-height: 1; margin-bottom: 0.5rem; }}
    .stat-desc {{ font-size: 0.82rem; color: var(--text-muted); }}
    .guide-cta {{ background: var(--bg-card); border: 1px solid var(--border); padding: 3rem; margin-top: 4rem; display: flex; justify-content: space-between; align-items: center; gap: 2rem; flex-wrap: wrap; }}
    .guide-cta h3 {{ font-family: var(--font-serif); font-size: 1.5rem; color: var(--text); }}
    @media (max-width: 900px) {{ .guide-grid {{ grid-template-columns: 1fr; gap: 3rem; }} .assessment-card {{ position: static; }} .stat-row {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
{NAV}

<div class="guide-hero">
  <div class="container">
    <div class="guide-hero-inner">
      <div class="guide-badge">&#9733; Free Executive Resource</div>
      <span class="label">Lead Magnet</span>
      <h1>The AI Workforce Readiness Guide</h1>
      <p>A practical framework for assessing your organization's readiness to deploy autonomous AI - and a step-by-step path for getting there.</p>
      <a href="#assessment" class="btn-primary">Start the Assessment</a>
    </div>
  </div>
</div>

<div class="guide-body">
  <div class="container">
    <div class="guide-grid">

      <!-- ASSESSMENT SIDEBAR -->
      <div>
        <div class="assessment-card" id="assessment">
          <h3>AI Readiness Assessment</h3>
          <p>Check each item that applies to your organization. Your readiness score updates in real time.</p>

          <div class="checklist-section">
            <h4>Infrastructure</h4>
            <ul class="checklist" id="checklistInfra">
              <li><span class="check-box" onclick="toggle(this)"></span> We use a CRM system with consistent data entry practices</li>
              <li><span class="check-box" onclick="toggle(this)"></span> Our team uses a shared email platform (Google Workspace or Microsoft 365)</li>
              <li><span class="check-box" onclick="toggle(this)"></span> We have a defined sales process with documented stages</li>
              <li><span class="check-box" onclick="toggle(this)"></span> We use a calendar system for scheduling and have a standard meeting link</li>
            </ul>
          </div>

          <div class="checklist-section">
            <h4>Operations</h4>
            <ul class="checklist" id="checklistOps">
              <li><span class="check-box" onclick="toggle(this)"></span> We can identify the three manual workflows that consume the most team time</li>
              <li><span class="check-box" onclick="toggle(this)"></span> Our lead follow-up process is defined but not consistently executed</li>
              <li><span class="check-box" onclick="toggle(this)"></span> We have revenue targets and track performance against them monthly</li>
              <li><span class="check-box" onclick="toggle(this)"></span> Our team spends time on tasks that could be replaced by automation</li>
            </ul>
          </div>

          <div class="checklist-section">
            <h4>Readiness</h4>
            <ul class="checklist" id="checklistReady">
              <li><span class="check-box" onclick="toggle(this)"></span> Leadership is aligned on AI as a strategic investment, not an experiment</li>
              <li><span class="check-box" onclick="toggle(this)"></span> We have a budget allocated or are prepared to allocate one for AI infrastructure</li>
              <li><span class="check-box" onclick="toggle(this)"></span> We have someone who can own the AI implementation internally</li>
              <li><span class="check-box" onclick="toggle(this)"></span> We are prepared to commit to a 90-day structured engagement</li>
            </ul>
          </div>

          <div class="score-bar">
            <div class="score-label">
              <span>Your Readiness Score</span>
              <span id="scoreNum">0 / 12</span>
            </div>
            <div class="score-track"><div class="score-fill" id="scoreFill"></div></div>
            <p class="score-text" id="scoreText">Check the items above that apply to your organization.</p>
          </div>
        </div>
      </div>

      <!-- GUIDE CONTENT -->
      <div class="guide-content">
        <h2>Why Most AI Initiatives Fail Before They Start</h2>
        <p>The failure rate for enterprise AI initiatives is frequently cited at 80%. That number is misleading because it conflates two very different kinds of failure: projects that fail because the technology was not capable, and projects that fail because the organization was not ready.</p>
        <p>In our experience, technology capability is rarely the limiting factor. The limiting factors are almost always organizational: unclear ownership, undefined success metrics, underestimated integration complexity, and insufficient commitment to the post-deployment optimization that makes AI systems actually work.</p>

        <div class="stat-row">
          <div class="stat-box"><span class="stat-num">80%</span><span class="stat-desc">of AI projects fail to reach production</span></div>
          <div class="stat-box"><span class="stat-num">28%</span><span class="stat-desc">of sales team time spent on manual data entry</span></div>
          <div class="stat-box"><span class="stat-num">21x</span><span class="stat-desc">higher lead qualification rate with 5-min response vs. 30-min</span></div>
        </div>

        <h2>The Four Readiness Dimensions</h2>

        <h3>1. Infrastructure Readiness</h3>
        <p>Autonomous AI agents need to connect to real systems with real data. A CRM with inconsistent data, an email platform without proper API access, or a telephony system that does not support programmatic integration all create friction that extends timelines and limits outcomes. Infrastructure readiness means your systems are in place, in use, and accessible for integration.</p>

        <h3>2. Operational Readiness</h3>
        <p>AI systems automate workflows. If your workflows are not defined, you cannot automate them. Operational readiness means you have a clear picture of your current processes - what they are, who performs them, how often, and what the expected output looks like. This does not require perfection. It requires documentation.</p>

        <h3>3. Organizational Readiness</h3>
        <p>The most technically sophisticated AI system will fail if it does not have an internal owner. Someone must be accountable for monitoring performance, escalating exceptions, and communicating results to leadership. This does not need to be a full-time role. It does need to be an explicit one.</p>

        <h3>4. Investment Readiness</h3>
        <p>AI systems integration is infrastructure spending, not software subscription spending. It requires a one-time build investment and ongoing optimization costs. Organizations that approach it with a trial-period mindset or an expectation of zero-cost implementation consistently underinvest and underperform. Investment readiness means understanding the financial commitment and having genuine leadership alignment around it.</p>

        <h2>What to Do With Your Score</h2>

        <h3>Score 0-4: Foundation First</h3>
        <p>Your priority is building the operational and infrastructure foundation that makes AI integration possible. Define your workflows. Get your CRM data clean. Establish ownership. Revisit AI deployment in 60-90 days after these foundations are in place. Premature AI deployment on weak foundations produces expensive failures.</p>

        <h3>Score 5-8: Strategic Planning Mode</h3>
        <p>You have the infrastructure and some operational clarity. The gaps are likely in organizational ownership or investment alignment. A strategy call would be productive at this stage - not to begin a deployment, but to get clarity on exactly what needs to happen before deployment can succeed. We can help you build that plan.</p>

        <h3>Score 9-12: Ready to Build</h3>
        <p>You have the infrastructure, the operational clarity, the organizational ownership, and the investment alignment to begin deployment. The question is not whether to invest in AI workforce automation - it is which workflows to start with and how to sequence the build for maximum early ROI. That is precisely what a strategy call is designed to answer.</p>

        <div class="guide-cta">
          <div>
            <h3>Know Your Score. Know Your Next Step.</h3>
            <p style="margin:0.5rem 0 0;">Schedule a 30-minute strategy call. We will walk through your assessment, identify your highest-leverage starting point, and give you a clear path forward.</p>
          </div>
          <a href="/book/" class="btn-primary" style="white-space:nowrap;">Book Strategy Call</a>
        </div>
      </div>
    </div>
  </div>
</div>

{FOOTER}
{BASE_JS}
<script>
  let checked = 0;
  const total = 12;
  const messages = ['Check the items above that apply to your organization.', 'Check the items above that apply to your organization.', 'Check the items above that apply to your organization.', 'Check the items above that apply to your organization.', 'Check the items above that apply to your organization.', 'You have some foundation in place. Keep going.', 'Good foundation. Operational clarity is building.', 'Strong infrastructure. Address the remaining gaps.', 'You are approaching deployment readiness.', 'Strong readiness. A few final items to address.', 'You are nearly fully ready for AI deployment.', 'Excellent readiness score. Time to build.', 'You are fully ready. Book your strategy call.'];
  function toggle(el) {{
    el.classList.toggle('checked');
    checked = document.querySelectorAll('.check-box.checked').length;
    document.getElementById('scoreNum').textContent = checked + ' / ' + total;
    document.getElementById('scoreFill').style.width = (checked / total * 100) + '%';
    document.getElementById('scoreText').textContent = messages[checked];
  }}
</script>
</body>
</html>"""


# ── WRITE ALL FILES ──
import os

# Blog posts
for post in POSTS:
    path = f"blog/{post['slug']}"
    os.makedirs(path, exist_ok=True)
    with open(f"{path}/index.html", "w") as f:
        f.write(make_blog_post(post))

# Blog index
os.makedirs("blog", exist_ok=True)
with open("blog/index.html", "w") as f:
    f.write(make_blog_index())

# Case studies
for study in CASE_STUDIES:
    path = f"case-studies/{study['slug']}"
    os.makedirs(path, exist_ok=True)
    with open(f"{path}/index.html", "w") as f:
        f.write(make_case_study(study))

# Case studies index
os.makedirs("case-studies", exist_ok=True)
with open("case-studies/index.html", "w") as f:
    f.write(make_case_studies_index())

# Booking page
os.makedirs("book", exist_ok=True)
with open("book/index.html", "w") as f:
    f.write(make_booking_page())

# Lead magnet / guide
os.makedirs("guide", exist_ok=True)
with open("guide/index.html", "w") as f:
    f.write(make_guide_page())

print("All files written.")
print(f"Blog posts: {len(POSTS)}")
print(f"Case studies: {len(CASE_STUDIES)}")
total_files = len(POSTS) + len(CASE_STUDIES) + 2 + 1 + 1  # posts + studies + indices + booking + guide
print(f"Total pages: {total_files}")