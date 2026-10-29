import os
import logging
from datetime import datetime

import cv2
import numpy as np
import easyocr
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO
from flask import Flask, request, jsonify, render_template, send_from_directory
from config import Config
from database import db, init_database
from models import InventoryLevel, ParkingSession, PaymentMethod, PlateDetection, Product, Sale, SaleItem, StockMovement

# ── App Setup ─────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger(__name__)

# ── Paths ──────────────────────────────────────────────────────────────────────
MODEL_PATH      = app.config["MODEL_PATH"]
FONT_BOLD       = os.path.join("static", "fonts", "Poppins-Bold.ttf")
FONT_REGULAR    = os.path.join("static", "fonts", "Poppins-Regular.ttf")
SLIPS_DIR       = app.config["SLIPS_DIR"]
os.makedirs(SLIPS_DIR, exist_ok=True)
init_database(app)

# ── Load Models Once ───────────────────────────────────────────────────────────
log.info("Loading YOLO model …")
yolo_model = YOLO(MODEL_PATH)
log.info("Loading EasyOCR reader …")
ocr_reader = easyocr.Reader(["en"], gpu=True)
log.info("Models ready.")


# ── Helpers ────────────────────────────────────────────────────────────────────
def detect_plate(image_np):
    """Run YOLO detection. Returns bounding box (x1,y1,x2,y2) or None."""
    results = yolo_model(image_np, save=False, verbose=False)
    boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
    if len(boxes) == 0:
        return None
    return tuple(boxes[0])  # (x1, y1, x2, y2)


def extract_text(image_np, box):
    """Crop detected plate and run EasyOCR. Returns (plate_text, cropped_img)."""
    x1, y1, x2, y2 = box
    pad = 4
    crop = image_np[
        max(0, y1 - pad): min(image_np.shape[0], y2 + pad),
        max(0, x1 - pad): min(image_np.shape[1], x2 + pad),
    ]
    if crop.size == 0:
        return "Crop Error", crop

    raw = ocr_reader.readtext(crop, detail=1, paragraph=False)
    log.info("EasyOCR raw: %s", raw)

    texts = [
        "".join(filter(str.isalnum, text)).upper()
        for (_, text, conf) in raw
        if conf >= 0.2
    ]
    plate_text = " ".join(t for t in texts if t) or "No text detected"
    return plate_text, crop


def generate_slip(plate_text, entry_time):
    """Draw a parking slip PNG. Returns the saved file path."""
    W, H = 600, 380
    BG       = "#0D0D1A"   # very dark navy (matches dashboard)
    PURPLE   = "#7C3AED"   # vivid purple accent
    PURPLE_L = "#A78BFA"   # light purple for labels
    WHITE    = "#FFFFFF"
    GRAY     = "#94A3B8"
    BORDER   = "#4C1D95"

    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Fonts
    try:
        f_title  = ImageFont.truetype(FONT_BOLD,    30)
        f_label  = ImageFont.truetype(FONT_REGULAR, 16)
        f_value  = ImageFont.truetype(FONT_BOLD,    18)
        f_small  = ImageFont.truetype(FONT_REGULAR, 12)
    except Exception:
        f_title = f_label = f_value = f_small = ImageFont.load_default()

    # Border
    draw.rounded_rectangle([12, 12, W - 12, H - 12], radius=14, outline=BORDER, width=2)

    # Purple accent bar at top
    draw.rounded_rectangle([12, 12, W - 12, 60], radius=14, fill=PURPLE)

    # Title
    title = "PARKING RECEIPT"
    bbox  = draw.textbbox((0, 0), title, font=f_title)
    draw.text(((W - (bbox[2] - bbox[0])) / 2, 18), title, font=f_title, fill=WHITE)

    # Divider
    draw.line([(40, 75), (W - 40, 75)], fill=BORDER, width=1)

    # Rows
    rows = [
        ("Vehicle Plate", plate_text),
        ("Entry Time",    entry_time.strftime("%d %b %Y  %H:%M:%S")),
        ("Parking Fee",   "Rs. 30.00"),
        ("Status",        "ACTIVE"),
    ]
    y = 95
    for label, value in rows:
        draw.text((50, y), label, font=f_label, fill=PURPLE_L)
        draw.text((270, y), value, font=f_value, fill=WHITE)
        y += 55

    # Footer
    footer = "Powered by Smart Parking System  •  YOLO + EasyOCR"
    bbox   = draw.textbbox((0, 0), footer, font=f_small)
    draw.text(((W - (bbox[2] - bbox[0])) / 2, H - 30), footer, font=f_small, fill=GRAY)

    # Save
    filename = f"slip_{plate_text.replace(' ', '_')}_{entry_time.strftime('%Y%m%d_%H%M%S')}.png"
    path     = os.path.join(SLIPS_DIR, filename)
    img.save(path)
    log.info("Slip saved: %s", path)
    return filename


# ── Routes ─────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/process", methods=["POST"])
@app.route("/api/detect", methods=["POST"])
def process():
    """Receive image → detect plate → OCR → generate slip → return JSON."""
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    # Decode image
    file_bytes = np.frombuffer(file.read(), dtype=np.uint8)
    img_bgr    = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if img_bgr is None:
        return jsonify({"error": "Could not decode image"}), 400

    # Detection
    box = detect_plate(img_bgr)
    if box is None:
        return jsonify({"error": "No number plate detected in image"}), 200

    # OCR
    plate_text, crop = extract_text(img_bgr, box)

    # Save annotated image for display
    annotated = img_bgr.copy()
    x1, y1, x2, y2 = box
    cv2.rectangle(annotated, (x1, y1), (x2, y2), (124, 58, 237), 3)
    anno_path = os.path.join(SLIPS_DIR, "annotated_latest.jpg")
    cv2.imwrite(anno_path, annotated)

    # Save cropped plate
    crop_path = os.path.join(SLIPS_DIR, "crop_latest.jpg")
    cv2.imwrite(crop_path, crop)

    # Generate slip
    entry_time  = datetime.now()
    slip_file   = generate_slip(plate_text, entry_time)
    detection = PlateDetection(plate_number=plate_text, image_path=anno_path, crop_path=crop_path)
    db.session.add(detection)
    db.session.flush()
    db.session.add(ParkingSession(
        plate_number=plate_text,
        detection_id=detection.id,
        entry_at=entry_time.strftime("%Y-%m-%d %H:%M:%S"),
        fee_amount=30,
        status="active",
    ))
    db.session.commit()

    return jsonify({
        "plate":      plate_text,
        "entry_time": entry_time.strftime("%d %b %Y, %H:%M:%S"),
        "fee":        "Rs. 30.00",
        "slip_url":   f"/static/slips/{slip_file}",
        "anno_url":   "/static/slips/annotated_latest.jpg",
        "crop_url":   "/static/slips/crop_latest.jpg",
    })


@app.route("/static/slips/<path:filename>")
def serve_slip(filename):
    return send_from_directory(SLIPS_DIR, filename)


@app.route("/history")
def history_page():
    return render_template("history.html")


@app.route("/api/history")
def history():
    sessions = db.session.query(ParkingSession).order_by(ParkingSession.id.desc()).limit(200).all()
    return jsonify([{
        "id": row.id,
        "plate": row.plate_number,
        "entry_time": row.entry_at,
        "exit_time": row.exit_at,
        "fee": float(row.fee_amount or 0),
        "status": row.status,
    } for row in sessions])


@app.route("/pos")
def pos_page():
    return render_template("pos.html")


@app.route("/api/products")
def products():
    rows = db.session.query(Product, InventoryLevel).join(InventoryLevel, InventoryLevel.product_id == Product.id).filter(Product.is_active == 1).order_by(Product.name).all()
    return jsonify([{
        "id": product.id,
        "name": product.name,
        "sku": product.sku,
        "price": float(product.price or 0),
        "stock": inventory.quantity_on_hand,
    } for product, inventory in rows])


@app.route("/sales")
def sales_page():
    return render_template("sales.html")


@app.route("/api/sales", methods=["GET", "POST"])
def sales():
    if request.method == "GET":
        rows = db.session.query(Sale).order_by(Sale.id.desc()).limit(200).all()
        return jsonify([{
            "id": row.id,
            "reference": row.reference,
            "subtotal": float(row.subtotal),
            "total": float(row.total),
            "status": row.status,
            "created_at": row.created_at,
        } for row in rows])

    payload = request.get_json(silent=True) or {}
    items = payload.get("items")
    if not isinstance(items, list) or not items:
        return jsonify({"error": "Add at least one product."}), 400

    try:
        quantities = {}
        for item in items:
            product_id = int(item["product_id"])
            quantity = int(item["quantity"])
            if quantity < 1:
                raise ValueError
            quantities[product_id] = quantities.get(product_id, 0) + quantity
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "Each item needs a valid product and quantity."}), 400

    cart = []
    for product_id, quantity in quantities.items():
        product = db.session.get(Product, product_id)
        stock = db.session.query(InventoryLevel).filter_by(product_id=product_id).first()
        if product is None or not product.is_active or stock is None:
            return jsonify({"error": "A selected product is unavailable."}), 404
        if stock.quantity_on_hand < quantity:
            return jsonify({"error": f"Not enough stock for {product.name}."}), 400
        cart.append((product, stock, quantity))

    subtotal = sum(float(product.price) * quantity for product, _, quantity in cart)
    method = db.session.query(PaymentMethod).filter_by(name=payload.get("payment_method", "Cash")).first()
    if method is None:
        return jsonify({"error": "Choose Cash or Card for payment."}), 400

    reference = f"POS-{datetime.now():%Y%m%d%H%M%S%f}"
    sale = Sale(reference=reference, subtotal=subtotal, tax_amount=0, total=subtotal,
                payment_method_id=method.id, status="paid")
    try:
        db.session.add(sale)
        db.session.flush()
        for product, stock, quantity in cart:
            db.session.add(SaleItem(sale_id=sale.id, product_id=product.id, quantity=quantity,
                                unit_price=product.price, line_total=float(product.price) * quantity))
            stock.quantity_on_hand -= quantity
            db.session.add(StockMovement(product_id=product.id, change_amount=-quantity,
                                         reason=f"Sale {reference}"))
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return jsonify({"id": sale.id, "reference": reference, "total": subtotal, "status": "paid"}), 201


@app.route("/api/sales/summary")
def sales_summary():
    from sqlalchemy import func

    today = datetime.now().strftime("%Y-%m-%d")
    count, total = db.session.query(func.count(Sale.id), func.coalesce(func.sum(Sale.total), 0)).filter(
        func.date(Sale.created_at) == today, Sale.status == "paid").one()
    return jsonify({"date": today, "transactions": count, "total_sales": float(total)})


@app.route("/api/dashboard/summary")
def dashboard_summary():
    from sqlalchemy import func

    today = datetime.now().strftime("%Y-%m-%d")
    visits = db.session.query(func.count(ParkingSession.id)).filter(
        func.date(ParkingSession.entry_at) == today).scalar()
    last = db.session.query(ParkingSession).order_by(ParkingSession.id.desc()).first()
    parking_fees = db.session.query(func.coalesce(func.sum(ParkingSession.fee_amount), 0)).filter(
        func.date(ParkingSession.entry_at) == today).scalar()
    sales_total = db.session.query(func.coalesce(func.sum(Sale.total), 0)).filter(
        func.date(Sale.created_at) == today, Sale.status == "paid").scalar()
    return jsonify({
        "vehicles": visits,
        "last_plate": last.plate_number if last else None,
        "revenue": float(parking_fees or 0) + float(sales_total or 0),
    })


# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(port=5000, use_reloader=False)
