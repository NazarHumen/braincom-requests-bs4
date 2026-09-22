# Task 1 - Requests / BS4

Parser for a product page on brain.com.ua (`requests` + `BeautifulSoup`), results are saved to PostgreSQL via Django ORM.

Run: `python modules/1_get_product_info.py`

## Project files

| File                             | Purpose                                                                 |
|----------------------------------|-------------------------------------------------------------------------|
| `parser_app/models.py`           | `Product` model — one row per parsed product: text fields, `ArrayField` for image links, `JSONField` for the full characteristics dictionary |
| `modules/load_django.py`         | Bootstraps Django for standalone scripts (adds the project to `sys.path`, sets `DJANGO_SETTINGS_MODULE`, calls `django.setup()`) so `modules/*.py` can use the ORM |
| `modules/1_get_product_info.py`  | The parser: requests the page, extracts the fields, prints them and saves them to the `Product` table |
| `results/parser_app_product.csv` | CSV export of the `Product` table (pgAdmin)                             |
| `results/braincom_project.dump`  | PostgreSQL dump of the database (pgAdmin, custom format)                |

## How the parser works

Every element is first located and verified manually in DevTools with XPath,
and only after that its class name is used in the code — the parser itself
works with `html.parser` and class names only (BS4 task).

| Field                    | Source                                                       |
|--------------------------|--------------------------------------------------------------|
| `title`                  | `h1.main-title`                                              |
| `price` / `sale_price`   | `div.main-price-block` → `div.br-pr-op` (old), `div.br-pr-np` (current) |
| `images`                 | `div.br-image-links` → `a.product-modal-button` → `img[src]` |
| `product_code`           | `span.br-pr-code-val`                                        |
| `reviews_count`          | `a.reviews-count` → `span`                                   |
| `color`, `memory`, `manufacturer`, `screen_diagonal`, `screen_resolution` | `div.br-pr-chr` → row by label text → next `span` |
| `characteristics`        | all `div.br-pr-chr-item` groups → `label: value` dictionary   |

Containers (`main-price-block`, `br-pr-chr`) are found once and reused.
Each field is wrapped in its own `try/except`, so a missing element does not
stop the script — the field is set to `None`.
