"""Static site builder for kalangaraitrust.org.

Usage (from the website folder):  python _build/build.py

- Each file in _build/pages/*.html is a page body with a front-matter comment at the top.
- Shared header/footer live in _build/partials/.
- Reports listed in _build/reports.json are rendered into annual-reports.html and it-reports.html.
- sitemap.xml (with image entries) is regenerated every build.
Folders starting with "_" are not published by GitHub Pages.
"""
import os, re, json, html, datetime, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(ROOT, '_build')
SITE = 'https://kalangaraitrust.org/'
TODAY = datetime.date.today().isoformat()
ORG = 'Kalangarai Charitable &amp; Educational Trust'


def read(*p):
    return open(os.path.join(*p), encoding='utf-8').read()


def front_matter(src):
    m = re.match(r'\s*<!--(.*?)-->\s*', src, re.S)
    meta = {}
    if m:
        for line in m.group(1).strip().splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                meta[k.strip()] = v.strip()
        src = src[m.end():]
    return meta, src


def url_for(slug):
    return SITE if slug == 'index' else f'{SITE}{slug}.html'


def head(meta, slug):
    title = meta['title']
    desc = meta['description']
    image = meta.get('image', 'images/og-kalangarai-ias-academy.jpg')
    url = url_for(slug)
    crumb = meta.get('crumb')
    ld = []
    if slug == 'index':
        ld.append(read(B, 'partials', 'org.jsonld').strip())
    if crumb:
        items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": SITE}]
        parent = meta.get('parent')
        if parent:
            pslug, pname = [x.strip() for x in parent.split('|')]
            items.append({"@type": "ListItem", "position": 2, "name": pname, "item": url_for(pslug)})
        items.append({"@type": "ListItem", "position": len(items) + 1, "name": html.unescape(crumb), "item": url})
        ld.append(json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}, ensure_ascii=False, indent=1))
    if meta.get('schema'):
        ld.append(read(B, 'partials', meta['schema']).strip())
    preload = ''
    if slug == 'index':
        preload = ('<link rel="preload" as="image" type="image/webp" fetchpriority="high" href="images/hero-kalangarai-ias-academy-1600.webp" '
                   'imagesrcset="images/hero-kalangarai-ias-academy-800.webp 800w, images/hero-kalangarai-ias-academy-1600.webp 1600w" imagesizes="100vw">\n')
    elif meta.get('preload'):
        preload = f'<link rel="preload" as="image" type="image/webp" fetchpriority="high" href="{meta["preload"]}">\n'
    ldtags = ''.join(f'<script type="application/ld+json">\n{x}\n</script>\n' for x in ld)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#004a85">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta name="robots" content="{meta.get('robots', 'index, follow, max-image-preview:large')}">
<link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta property="og:type" content="{meta.get('type', 'website')}">
<meta property="og:site_name" content="{ORG}">
<meta property="og:title" content="{meta.get('og_title', title)}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}{image}">
<meta property="og:locale" content="en_IN">
<meta property="og:locale:alternate" content="ta_IN">
<meta property="og:locale:alternate" content="hi_IN">
<meta name="twitter:card" content="summary_large_image">
{preload}{ldtags}<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Noto+Sans+Tamil:wght@400;500;600;700;800&family=Noto+Sans+Devanagari:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/site.css?v={VERSION}">
</head>
<body class="page-{slug}">
'''


def mark_nav(header, meta):
    nav = meta.get('nav')
    marked = False
    if nav and f'data-nav="{nav}" class="' in header:  # link already has a class (e.g. the Evening School pill)
        header = re.sub(f'data-nav="{nav}" class="([^"]*)"', f'data-nav="{nav}" class="\\1 active" aria-current="page"', header, count=1)
        marked = True
    elif nav and f'data-nav="{nav}"' in header:
        header = header.replace(f'data-nav="{nav}"', f'data-nav="{nav}" class="active" aria-current="page"', 1)
        marked = f'data-nav="{nav}" class="active" aria-current="page" data-navgroup' not in header
    group = meta.get('group')
    if group and not marked and f'data-navgroup="{group}"' in header:  # plain top-level link for the whole section
        header = header.replace(f'data-navgroup="{group}"', f'data-navgroup="{group}" class="active"', 1)
    if group:
        header = header.replace(f'<div class="dd" data-group="{group}">', f'<div class="dd current" data-group="{group}">', 1)
    return header


def breadcrumb(meta):
    crumb = meta.get('crumb')
    if not crumb:
        return ''
    parts = ['<a href="index.html" data-en="Home" data-ta="முகப்பு" data-hi="होम">Home</a>']
    if meta.get('parent'):
        pslug, pname = [x.strip() for x in meta['parent'].split('|')]
        parts.append(f'<a href="{pslug}.html">{pname}</a>')
    parts.append(f'<span aria-current="page">{crumb}</span>')
    return '<nav class="crumbs" aria-label="Breadcrumb">' + ' <i>›</i> '.join(parts) + '</nav>'


def page_hero(meta):
    """Standard inner-page banner, built from front matter keys hero_*."""
    if 'hero_title' not in meta:
        return ''
    bg = meta.get('hero_image', 'images/trust-members-students-free-training-centre.webp')
    t = meta['hero_title']; tag = meta.get('hero_tag', '')
    def tri(key, default):
        en = meta.get(key, default)
        ta = meta.get(key + '_ta'); hi = meta.get(key + '_hi')
        attrs = f' data-en="{en}"' + (f' data-ta="{ta}" data-hi="{hi}"' if ta and hi else '')
        return attrs, en
    ta_attrs, t_en = tri('hero_title', t)
    tag_attrs, tag_en = tri('hero_tag', tag)
    sub_attrs, sub_en = tri('hero_sub', meta.get('hero_sub', ''))
    # background set inline so the image path resolves from the page, not from the stylesheet folder
    style = f"background-image:linear-gradient(100deg,rgba(6,33,62,.95) 0%,rgba(6,33,62,.82) 55%,rgba(6,33,62,.5) 100%),url('{bg}')"
    return f'''<section class="page-hero" style="{style}">
  <div class="container">
    {breadcrumb(meta)}
    {f'<span class="hero-tag"{tag_attrs}>{tag_en}</span>' if tag_en else ''}
    <h1{ta_attrs}>{t_en}</h1>
    {f'<p{sub_attrs}>{sub_en}</p>' if sub_en else ''}
  </div>
</section>
'''


def render_reports(src):
    data = json.loads(read(B, 'reports.json'))

    def rows(items, empty):
        if not items:
            return f'<p class="empty">{empty}</p>'
        out = []
        for r in items:
            size = ''
            f = r.get('file')
            if f and os.path.exists(os.path.join(ROOT, f)):
                size = f'{os.path.getsize(os.path.join(ROOT, f)) / 1048576:.1f} MB PDF'
            if f:
                actions = ''
                if r.get('view'):
                    actions += f'<a class="btn btn-outline btn-sm" href="{r["view"]}">View online</a>'
                actions += f'<a class="btn btn-sm" href="{f}" download>⬇ Download</a>'
                status = size
            else:
                actions = '<a class="btn btn-outline btn-sm" href="contact.html">Request a copy</a>'
                status = r.get('status', 'Available on request')
            out.append(f'''<div class="report-row">
  <div class="report-icon" aria-hidden="true">📄</div>
  <div class="report-info"><b>{r['title']}</b><span>{r.get('period', '')}{' · ' if r.get('period') and status else ''}{status}</span>{f"<p>{r['note']}</p>" if r.get('note') else ''}</div>
  <div class="report-actions">{actions}</div>
</div>''')
        return '\n'.join(out)
    src = src.replace('{{ANNUAL_REPORTS}}', rows(data['annual'], 'Annual reports will be published here.'))
    src = src.replace('{{IT_REPORTS}}', rows(data['it'], 'Income-tax returns will be published here as they are uploaded.'))
    return src


def render_report_viewer(src):
    n = len([f for f in os.listdir(os.path.join(ROOT, 'annual-report')) if f.endswith('.webp')])
    figs = []
    for i in range(1, n + 1):
        attrs = 'loading="lazy" ' if i > 2 else ('fetchpriority="high" ' if i == 1 else '')
        alt = ('Cover of the Kalangarai Charitable and Educational Trust Impact Journey Report 2018–26' if i == 1
               else f'Kalangarai Impact Journey Report 2018–26, page {i} of {n}')
        figs.append(f'    <figure id="page-{i}" class="report-page"><img src="annual-report/kalangarai-annual-report-page-{i:02d}.webp" width="1000" height="1414" alt="{alt}" {attrs}decoding="async"><figcaption>Page {i} / {n}</figcaption></figure>')
    pdf = 'annual-report/kalangarai-impact-journey-report-2018-26.pdf'
    size = f'{os.path.getsize(os.path.join(ROOT, pdf)) / 1048576:.0f} MB'
    return src.replace('{{REPORT_PAGES}}', '\n'.join(figs)).replace('{{PDF_SIZE}}', size).replace('{{PAGE_COUNT}}', str(n))


VERSION = datetime.datetime.now().strftime('%Y%m%d%H%M')

try:
    from PIL import Image  # optional: adds width/height to images so the layout doesn't jump
except ImportError:
    Image = None
_dims = {}


def size_images(doc):
    def fix(m):
        tag = m.group(0)
        if ' width=' in tag or Image is None:
            return tag
        src = re.search(r'src="([^"]+)"', tag)
        if not src or src.group(1).startswith('http'):
            return tag
        path = os.path.join(ROOT, src.group(1))
        if path not in _dims:
            try:
                _dims[path] = Image.open(path).size
            except Exception:
                _dims[path] = None
        if not _dims[path]:
            return tag
        w, h = _dims[path]
        return tag.replace('<img ', f'<img width="{w}" height="{h}" ', 1)
    return re.sub(r'<img [^>]*>', fix, doc)


def build():
    header = read(B, 'partials', 'header.html')
    footer = read(B, 'partials', 'footer.html')
    pages = sorted(f for f in os.listdir(os.path.join(B, 'pages')) if f.endswith('.html'))
    sitemap = []
    for f in pages:
        slug = f[:-5]
        meta, body = front_matter(read(B, 'pages', f))
        if '{{ANNUAL_REPORTS}}' in body or '{{IT_REPORTS}}' in body:
            body = render_reports(body)
        if '{{REPORT_PAGES}}' in body:
            body = render_report_viewer(body)
        doc = (head(meta, slug) + mark_nav(header, meta) + '\n<main id="main">\n' + page_hero(meta) + body.strip()
               + '\n</main>\n\n' + footer + f'\n<script src="assets/js/site.js?v={VERSION}"></script>\n</body>\n</html>\n')
        doc = size_images(doc)
        if slug == '404':  # served at any URL depth, so resolve links from the site root
            doc = doc.replace('<meta charset="UTF-8">', '<meta charset="UTF-8">\n<base href="/">', 1)
        for missing in re.findall(r'(?:src|href)="((?:images|annual-report|assets)/[^"?#]+)', doc):
            if not os.path.exists(os.path.join(ROOT, missing)):
                print(f'  !! {f}: missing file {missing}')
        for link in re.findall(r'href="([a-z0-9-]+\.html)', doc):
            if not os.path.exists(os.path.join(B, 'pages', link)):
                print(f'  !! {f}: link to unknown page {link}')
        open(os.path.join(ROOT, f), 'w', encoding='utf-8', newline='\n').write(doc)
        if meta.get('robots', '').startswith('noindex'):
            continue
        imgs = []
        for src in re.findall(r'<img [^>]*src="(images/[^"]+|annual-report/[^"]+)"', doc):
            if src not in imgs and 'logo' not in src:
                imgs.append(src)
        sitemap.append((url_for(slug), meta.get('priority', '0.7'), imgs[:30]))
        print(f'  built {f:38s} {len(doc.encode()) // 1024:4d} KB  {len(imgs):3d} images')
    # sitemap with image entries + the PDF report
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
    for loc, pr, imgs in sorted(sitemap, key=lambda x: (-float(x[1]), x[0])):
        lines.append(f'  <url>\n    <loc>{loc}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <priority>{pr}</priority>')
        for i in imgs:
            lines.append(f'    <image:image><image:loc>{SITE}{i}</image:loc></image:image>')
        lines.append('  </url>')
    lines.append(f'  <url>\n    <loc>{SITE}annual-report/kalangarai-impact-journey-report-2018-26.pdf</loc>\n    <lastmod>{TODAY}</lastmod>\n    <priority>0.5</priority>\n  </url>')
    lines.append('</urlset>')
    open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
    print(f'  sitemap.xml: {len(sitemap) + 1} URLs')


if __name__ == '__main__':
    build()
