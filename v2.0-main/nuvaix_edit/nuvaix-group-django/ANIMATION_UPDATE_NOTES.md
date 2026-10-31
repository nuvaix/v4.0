# NUVAIX live topic rotation update

This update adds a shared topic spotlight to every page, cycling through Businesses, Technology, and NUVAIX Paint every 3 seconds. It includes manual arrow/dot controls, keyboard focus support, hover/focus pause, hidden-tab pause, and reduced-motion support. The homepage hero also advances every 3 seconds.

## Files changed
- `core/templates/core/base.html`
- `core/static/core/css/site.css`
- `core/static/core/js/site.js`

## Apply to an existing checkout
Merge the `core/` directory from `nuvaix-animation-update.zip` into the project directory containing `manage.py`, preserving the paths. Then run:

```bash
python manage.py collectstatic --noinput
python manage.py check
python manage.py runserver 8001
```

The topic links use the existing Django URL names `businesses`, `technology`, and `paint`. No additional JavaScript package or plugin is required.
