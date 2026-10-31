# NUVAIX ground-up visual redesign

This update replaces the previous visual theme with a premium midnight-navy, champagne-gold and glass interface. It retains the Django URL names, view/template structure, forms and business content.

## Design changes

- Oversized original NUVAIX logo in the glass sticky navigation and footer; duplicated text logo removed.
- New full-site design tokens, high-contrast typography, layered glass surfaces, luminous gold accents and responsive spacing.
- Three-dimensional geometric hero artwork, floating interface elements and a more cinematic hero slide transition.
- Inner-page headings animate in with a 3D flip/tilt effect.
- NUVAIX Paint uses the existing branded product-concept image inside a perspective card. The page already labels this artwork as a concept, not confirmed inventory.
- JavaScript-powered scroll reveals, pointer-responsive 3D card tilt, reading-progress line, mobile navigation, and an internal page-transition curtain.
- GSAP and ScrollTrigger are loaded as optional animation enhancements. If the CDN is unavailable, the site's native JavaScript/CSS effects continue to work.
- Reduced-motion preferences are respected, and the layout adapts for mobile, tablet and desktop.

## Apply the update

Extract `nuvaix-groundup-update.zip` into the directory containing `manage.py`, merging the `core` directory and replacing the listed files. Back up your project first.

```bash
python3 manage.py check
python3 manage.py collectstatic --noinput
python3 manage.py runserver 8001
```

Open `http://127.0.0.1:8001/` and force-refresh the browser with Ctrl+F5.

## Notes

This is a frontend redesign; it does not replace the Django data model, routes, contact handling or business logic. The original paint packaging visual is explicitly presented as concept artwork. Production deployment should serve static files over HTTPS and confirm that third-party CDN scripts are permitted by the site's Content Security Policy.
