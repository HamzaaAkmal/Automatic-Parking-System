from database import db


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True)
    password_hash = db.Column(db.String)
    is_active = db.Column(db.Boolean, nullable=False, server_default=db.text("1"))
    created_at = db.Column(db.String, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))


class UserRole(db.Model):
    __tablename__ = "user_roles"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), primary_key=True)


class Employee(db.Model):
    __tablename__ = "employees"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    job_title = db.Column(db.String)
    hired_at = db.Column(db.String)
    is_active = db.Column(db.Boolean, nullable=False, server_default=db.text("1"))


class Customer(db.Model):
    __tablename__ = "customers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, unique=True)
    email = db.Column(db.String)
    created_at = db.Column(db.String, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))


class VehicleType(db.Model):
    __tablename__ = "vehicle_types"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)


class VehicleMake(db.Model):
    __tablename__ = "vehicle_makes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)


class VehicleModel(db.Model):
    __tablename__ = "vehicle_models"
    id = db.Column(db.Integer, primary_key=True)
    make_id = db.Column(db.Integer, db.ForeignKey("vehicle_makes.id"))
    name = db.Column(db.String, nullable=False)


class CustomerVehicle(db.Model):
    __tablename__ = "customer_vehicles"
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"))
    type_id = db.Column(db.Integer, db.ForeignKey("vehicle_types.id"))
    model_id = db.Column(db.Integer, db.ForeignKey("vehicle_models.id"))
    plate_number = db.Column(db.String, nullable=False, unique=True)


class ParkingLot(db.Model):
    __tablename__ = "parking_lots"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String)
    is_active = db.Column(db.Boolean, nullable=False, server_default=db.text("1"))


class ParkingZone(db.Model):
    __tablename__ = "parking_zones"
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey("parking_lots.id"), nullable=False)
    name = db.Column(db.String, nullable=False)


class ParkingSpot(db.Model):
    __tablename__ = "parking_spots"
    id = db.Column(db.Integer, primary_key=True)
    zone_id = db.Column(db.Integer, db.ForeignKey("parking_zones.id"), nullable=False)
    label = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False, server_default=db.text("'available'"))


class Camera(db.Model):
    __tablename__ = "cameras"
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey("parking_lots.id"))
    name = db.Column(db.String, nullable=False)
    location = db.Column(db.String)
    is_active = db.Column(db.Boolean, nullable=False, server_default=db.text("1"))


class Barrier(db.Model):
    __tablename__ = "barriers"
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey("parking_lots.id"))
    name = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False, server_default=db.text("'closed'"))


class PlateDetection(db.Model):
    __tablename__ = "plate_detections"
    id = db.Column(db.Integer, primary_key=True)
    camera_id = db.Column(db.Integer, db.ForeignKey("cameras.id"))
    plate_number = db.Column(db.String, nullable=False)
    confidence = db.Column(db.Float)
    image_path = db.Column(db.String)
    crop_path = db.Column(db.String)
    created_at = db.Column(db.String, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))


class ParkingSession(db.Model):
    __tablename__ = "parking_sessions"
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("customer_vehicles.id"))
    spot_id = db.Column(db.Integer, db.ForeignKey("parking_spots.id"))
    detection_id = db.Column(db.Integer, db.ForeignKey("plate_detections.id"))
    plate_number = db.Column(db.String, nullable=False)
    entry_at = db.Column(db.String, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))
    exit_at = db.Column(db.String)
    fee_amount = db.Column(db.Numeric, nullable=False, server_default=db.text("30"))
    status = db.Column(db.String, nullable=False, server_default=db.text("'active'"))


class AccessLog(db.Model):
    __tablename__ = "access_logs"
    id = db.Column(db.Integer, primary_key=True)
    barrier_id = db.Column(db.Integer, db.ForeignKey("barriers.id"))
    detection_id = db.Column(db.Integer, db.ForeignKey("plate_detections.id"))
    action = db.Column(db.String, nullable=False)
    created_at = db.Column(db.String, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))


class RatePlan(db.Model):
    __tablename__ = "rate_plans"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, server_default=db.text("1"))


class RateRule(db.Model):
    __tablename__ = "rate_rules"
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey("rate_plans.id"), nullable=False)
    vehicle_type_id = db.Column(db.Integer, db.ForeignKey("vehicle_types.id"))
    hourly_rate = db.Column(db.Numeric, nullable=False, server_default=db.text("30"))


class Tariff(db.Model):
    __tablename__ = "tariffs"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    rate = db.Column(db.Numeric, nullable=False)
    starts_at = db.Column(db.String)
    ends_at = db.Column(db.String)


class Reservation(db.Model):
    __tablename__ = "reservations"
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    lot_id = db.Column(db.Integer, db.ForeignKey("parking_lots.id"), nullable=False)
    starts_at = db.Column(db.String, nullable=False)
    ends_at = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False, server_default=db.text("'booked'"))


class ReservationSpot(db.Model):
    __tablename__ = "reservation_spots"
    reservation_id = db.Column(db.Integer, db.ForeignKey("reservations.id"), primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey("parking_spots.id"), primary_key=True)


class Invoice(db.Model):
    __tablename__ = "invoices"
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"))
    session_id = db.Column(db.Integer, db.ForeignKey("parking_sessions.id"))
    subtotal = db.Column(db.Numeric, nullable=False, server_default=db.text("0"))
    tax_amount = db.Column(db.Numeric, nullable=False, server_default=db.text("0"))
    total = db.Column(db.Numeric, nullable=False, server_default=db.text("0"))
    created_at = db.Column(db.String, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))


class InvoiceItem(db.Model):
    __tablename__ = "invoice_items"
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoices.id"), nullable=False)
    description = db.Column(db.String, nullable=False)
    quantity = db.Column(db.Numeric, nullable=False, server_default=db.text("1"))
    unit_price = db.Column(db.Numeric, nullable=False, server_default=db.text("0"))


class PaymentMethod(db.Model):
    __tablename__ = "payment_methods"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    is_active = db.Column(db.Boolean, nullable=False, server_default=db.text("1"))


class Payment(db.Model):
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoices.id"))
    method_id = db.Column(db.Integer, db.ForeignKey("payment_methods.id"))
    amount = db.Column(db.Numeric, nullable=False)
    status = db.Column(db.String, nullable=False, server_default=db.text("'paid'"))
    created_at = db.Column(db.String, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))


class Refund(db.Model):
    __tablename__ = "refunds"
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey("payments.id"), nullable=False)
    amount = db.Column(db.Numeric, nullable=False)
    reason = db.Column(db.String)
    created_at = db.Column(db.String, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))


class CashRegister(db.Model):
    __tablename__ = "cash_registers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    opening_balance = db.Column(db.Numeric, nullable=False, server_default=db.text("0"))
    is_open = db.Column(db.Boolean, nullable=False, server_default=db.text("0"))


class Shift(db.Model):
    __tablename__ = "shifts"
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"))
    register_id = db.Column(db.Integer, db.ForeignKey("cash_registers.id"))
    opened_at = db.Column(db.String, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))
    closed_at = db.Column(db.String)
    closing_balance = db.Column(db.Numeric)


class ProductCategory(db.Model):
    __tablename__ = "product_categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("product_categories.id"))
    name = db.Column(db.String, nullable=False)
    sku = db.Column(db.String, nullable=False, unique=True)
    price = db.Column(db.Numeric, nullable=False, server_default=db.text("0"))
    is_active = db.Column(db.Boolean, nullable=False, server_default=db.text("1"))


class InventoryLevel(db.Model):
    __tablename__ = "inventory_levels"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, unique=True)
    quantity_on_hand = db.Column(db.Integer, nullable=False, server_default=db.text("0"))


class Supplier(db.Model):
    __tablename__ = "suppliers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String)
    email = db.Column(db.String)


class PurchaseOrder(db.Model):
    __tablename__ = "purchase_orders"
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.id"))
    status = db.Column(db.String, nullable=False, server_default=db.text("'open'"))
    created_at = db.Column(db.String, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))


class PurchaseOrderItem(db.Model):
    __tablename__ = "purchase_order_items"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("purchase_orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Numeric, nullable=False)


class StockMovement(db.Model):
    __tablename__ = "stock_movements"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    change_amount = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String, nullable=False)
    created_at = db.Column(db.String, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))


class Tax(db.Model):
    __tablename__ = "taxes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    rate = db.Column(db.Numeric, nullable=False, server_default=db.text("0"))
    is_active = db.Column(db.Boolean, nullable=False, server_default=db.text("1"))


class Coupon(db.Model):
    __tablename__ = "coupons"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, nullable=False, unique=True)
    discount_percent = db.Column(db.Numeric, nullable=False, server_default=db.text("0"))
    is_active = db.Column(db.Boolean, nullable=False, server_default=db.text("1"))


class CustomerCoupon(db.Model):
    __tablename__ = "customer_coupons"
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), primary_key=True)
    coupon_id = db.Column(db.Integer, db.ForeignKey("coupons.id"), primary_key=True)
    used_at = db.Column(db.String)


class Sale(db.Model):
    __tablename__ = "sales"
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String, nullable=False, unique=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"))
    shift_id = db.Column(db.Integer, db.ForeignKey("shifts.id"))
    payment_method_id = db.Column(db.Integer, db.ForeignKey("payment_methods.id"))
    subtotal = db.Column(db.Numeric, nullable=False)
    tax_amount = db.Column(db.Numeric, nullable=False, server_default=db.text("0"))
    total = db.Column(db.Numeric, nullable=False)
    status = db.Column(db.String, nullable=False, server_default=db.text("'paid'"))
    created_at = db.Column(db.String, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))


class SaleItem(db.Model):
    __tablename__ = "sale_items"
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey("sales.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric, nullable=False)
    line_total = db.Column(db.Numeric, nullable=False)


class ExpenseCategory(db.Model):
    __tablename__ = "expense_categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)


class Expense(db.Model):
    __tablename__ = "expenses"
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("expense_categories.id"))
    description = db.Column(db.String, nullable=False)
    amount = db.Column(db.Numeric, nullable=False)
    created_at = db.Column(db.String, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))


class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    message = db.Column(db.String, nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, server_default=db.text("0"))
    created_at = db.Column(db.String, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))


class Setting(db.Model):
    __tablename__ = "settings"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    value = db.Column(db.String)


class AuditLog(db.Model):
    __tablename__ = "audit_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    action = db.Column(db.String, nullable=False)
    details = db.Column(db.String)
    created_at = db.Column(db.String, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))


class DailySummary(db.Model):
    __tablename__ = "daily_summaries"
    id = db.Column(db.Integer, primary_key=True)
    summary_date = db.Column(db.String, nullable=False, unique=True)
    vehicle_count = db.Column(db.Integer, nullable=False, server_default=db.text("0"))
    sales_total = db.Column(db.Numeric, nullable=False, server_default=db.text("0"))
    parking_total = db.Column(db.Numeric, nullable=False, server_default=db.text("0"))


class LoyaltyAccount(db.Model):
    __tablename__ = "loyalty_accounts"
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False, unique=True)
    points = db.Column(db.Integer, nullable=False, server_default=db.text("0"))


class LoyaltyTransaction(db.Model):
    __tablename__ = "loyalty_transactions"
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("loyalty_accounts.id"), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String, nullable=False)
    created_at = db.Column(db.String, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))


class SystemEvent(db.Model):
    __tablename__ = "system_events"
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String, nullable=False)
    details = db.Column(db.String)
    created_at = db.Column(db.String, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))
