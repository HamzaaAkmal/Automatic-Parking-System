# Smart Parking System

Flask app for number plate detection, parking history and counter sales. SQLite stores the records; SQLAlchemy maps the database tables for app queries.

## Run locally

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
./.venv/bin/python app.py
```

Open `http://127.0.0.1:5000`. The first start downloads EasyOCR's English models. The database is created at `instance/parking.db` from `schema.sql` and is safe to initialize more than once. The POS has three sample products to get started.

## Pages and routes

| Page or route | Purpose |
| --- | --- |
| `/` | Plate scan dashboard |
| `POST /process` or `POST /api/detect` | Detect a plate, make a parking slip and save the visit |
| `/history` and `GET /api/history` | Recent parking visits |
| `/pos` and `GET /api/products` | Create a point-of-sale cart |
| `POST /api/sales` | Complete a sale, record line items and update stock |
| `/sales`, `GET /api/sales` | Recent sales |
| `GET /api/sales/summary` | Today's paid POS total and transaction count |

`POST /api/sales` accepts JSON with a `payment_method` (`Cash` or `Card`) and an `items` list:

```json
{"payment_method":"Cash","items":[{"product_id":1,"quantity":2}]}
```

`schema.sql` defines 50 tables. Their SQLAlchemy ORM classes are in `models.py`, and the routes use those classes to save visits, sales and stock changes. The app creates the local database at startup and seeds three sample products. Keep the database file out of source control; remove `instance/parking.db` only when you want a fresh local database.
