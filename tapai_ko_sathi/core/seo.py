from django.http import HttpResponse
from django.urls import reverse


def robots_txt(request):
    """
    Minimal robots.txt allowing all well-behaved crawlers.
    """
    lines = [
        "User-agent: *",
        "Disallow:",
        f"Sitemap: {request.build_absolute_uri(reverse('sitemap_xml'))}",
        "",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_xml(request):
    """
    Simple XML sitemap for key pages and product listing.
    For production you might expand this to include all products.
    """
    base = request.build_absolute_uri("/")
    urls = [
        "",
        "products/",
        "accounts/login/",
        "accounts/signup/",
        "cart/",
    ]
    xml_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for path in urls:
        loc = base + path
        xml_parts.append("  <url>")
        xml_parts.append(f"    <loc>{loc}</loc>")
        xml_parts.append("  </url>")
    xml_parts.append("</urlset>")
    return HttpResponse("\n".join(xml_parts), content_type="application/xml")

