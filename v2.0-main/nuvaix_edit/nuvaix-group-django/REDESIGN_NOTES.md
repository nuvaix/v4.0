# NUVAIX Next visual redesign

This update replaces the previous visual treatment with a more editorial, high-contrast NUVAIX interface: deep midnight navy, metallic gold, glass surfaces, large typography, a more prominent existing logo, dimensional cards, and responsive layouts.

## Interactive behaviour

- The shared Business / Technology / NUVAIX Paint spotlight remains available across pages and rotates automatically; its previous/next and dot controls work where shown.
- The homepage hero keeps its manual and automatic controls, with updated styling and depth.
- JavaScript applies directional reveal animations to page sections, headings, cards, forms, and content blocks as they enter the viewport across the site.
- Cards respond to pointer movement with a restrained 3D tilt and light reflection on compatible desktop devices.
- A gold reading-progress line follows scroll position.
- Navigation remains responsive, and animations respect `prefers-reduced-motion`.

## Files changed

- `core/static/core/css/site.css` — visual redesign and responsive motion styles.
- `core/static/core/js/site.js` — shared scroll reveal, progress indicator and 3D card interaction.

No external animation library is required. The existing Django templates, routes, forms, logo asset, and backend behaviour are retained.
