import os
import uuid
import secrets
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import desc

from config_database import engine, Base, get_database_session, SessionLocal
import inventory_models as models

# --- SECURITY CONFIGURATION ---
ADMIN_MASTER_PIN = "kushalex@2026"  # Change to your preferred store passcode
ACTIVE_SESSIONS = set()

def verify_session_token(x_auth_token: Optional[str] = Header(None)):
    if not x_auth_token or x_auth_token not in ACTIVE_SESSIONS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session locked or unauthorized. Please unlock with PIN."
        )
    return True

# Initialize database schema
Base.metadata.create_all(bind=engine)

def seed_realistic_pharmacy_catalog():
    db = SessionLocal()
    try:
        default_inventory = [
            {
                "brand_name": "Amoxil", "generic_name": "Amoxicillin", "dosage": "500mg",
                "dosage_form": "Capsule", "dispense_unit": "Capsule", "units_per_strip": 10, "strips_per_box": 10,
                "batch_no": "AMX-801", "exp_days": 450, "packages_received": 10, "package_cost": 220.0, "unit_price": 3.00
            },
            {
                "brand_name": "Panadol Extra", "generic_name": "Paracetamol + Caffeine", "dosage": "500mg/65mg",
                "dosage_form": "Tablet", "dispense_unit": "Tablet", "units_per_strip": 12, "strips_per_box": 8,
                "batch_no": "PAN-921", "exp_days": 650, "packages_received": 15, "package_cost": 95.0, "unit_price": 1.50
            },
            {
                "brand_name": "Cipro", "generic_name": "Ciprofloxacin", "dosage": "500mg",
                "dosage_form": "Tablet", "dispense_unit": "Tablet", "units_per_strip": 10, "strips_per_box": 2,
                "batch_no": "CPR-104", "exp_days": 360, "packages_received": 12, "package_cost": 85.0, "unit_price": 5.50
            },
            {
                "brand_name": "Brufen", "generic_name": "Ibuprofen", "dosage": "400mg",
                "dosage_form": "Tablet", "dispense_unit": "Tablet", "units_per_strip": 10, "strips_per_box": 10,
                "batch_no": "BRU-440", "exp_days": 520, "packages_received": 10, "package_cost": 140.0, "unit_price": 2.00
            },
            {
                "brand_name": "Metformin", "generic_name": "Metformin Hydrochloride", "dosage": "500mg",
                "dosage_form": "Tablet", "dispense_unit": "Tablet", "units_per_strip": 10, "strips_per_box": 10,
                "batch_no": "MTF-501", "exp_days": 550, "packages_received": 10, "package_cost": 150.0, "unit_price": 2.00
            },
            {
                "brand_name": "Amoxicillin Oral Suspension", "generic_name": "Amoxicillin Trihydrate", "dosage": "125mg/5mL (100mL)",
                "dosage_form": "Syrup", "dispense_unit": "Bottle", "units_per_strip": 1, "strips_per_box": 1,
                "batch_no": "AMX-SYR-01", "exp_days": 320, "packages_received": 25, "package_cost": 65.0, "unit_price": 95.00
            },
            {
                "brand_name": "Paracetamol Paediatric Syrup", "generic_name": "Paracetamol", "dosage": "120mg/5mL (60mL)",
                "dosage_form": "Syrup", "dispense_unit": "Bottle", "units_per_strip": 1, "strips_per_box": 1,
                "batch_no": "PCM-SYR-04", "exp_days": 540, "packages_received": 30, "package_cost": 35.0, "unit_price": 55.00
            },
            {
                "brand_name": "Hydrocortisone Cream", "generic_name": "Hydrocortisone 1%", "dosage": "15g Tube",
                "dosage_form": "Ointment", "dispense_unit": "Tube", "units_per_strip": 1, "strips_per_box": 1,
                "batch_no": "HYD-CRM-11", "exp_days": 490, "packages_received": 20, "package_cost": 40.0, "unit_price": 65.00
            },
            {
                "brand_name": "Diclofenac Injection", "generic_name": "Diclofenac Sodium", "dosage": "75mg/3mL",
                "dosage_form": "Injection", "dispense_unit": "Ampoule", "units_per_strip": 5, "strips_per_box": 10,
                "batch_no": "DIC-INJ-88", "exp_days": 410, "packages_received": 5, "package_cost": 150.0, "unit_price": 12.00
            },
            {
                "brand_name": "Gentamicin Eye/Ear Drops", "generic_name": "Gentamicin Sulfate 0.3%", "dosage": "10mL Bottle",
                "dosage_form": "Drops", "dispense_unit": "Bottle", "units_per_strip": 1, "strips_per_box": 1,
                "batch_no": "GEN-DRP-02", "exp_days": 380, "packages_received": 20, "package_cost": 30.0, "unit_price": 48.00
            },
            {
                "brand_name": "Normal Saline 0.9%", "generic_name": "Sodium Chloride 0.9%", "dosage": "500mL IV Bag",
                "dosage_form": "IV Fluid", "dispense_unit": "Bag", "units_per_strip": 1, "strips_per_box": 20,
                "batch_no": "NS-500-77", "exp_days": 600, "packages_received": 4, "package_cost": 500.0, "unit_price": 40.00
            }
        ]

        for item in default_inventory:
            existing = db.query(models.MedicineCatalog).filter(
                models.MedicineCatalog.brand_name == item["brand_name"]
            ).first()

            if not existing:
                med = models.MedicineCatalog(
                    brand_name=item["brand_name"],
                    generic_name=item["generic_name"],
                    dosage=item["dosage"],
                    dosage_form=item["dosage_form"],
                    dispense_unit=item["dispense_unit"],
                    units_per_strip=item["units_per_strip"],
                    strips_per_box=item["strips_per_box"]
                )
                db.add(med)
                db.commit()
                db.refresh(med)

                units_per_pack = item["units_per_strip"] * item["strips_per_box"]
                total_base_units = item["packages_received"] * units_per_pack

                price_strip = round(item["unit_price"] * item["units_per_strip"], 2) if item["units_per_strip"] > 1 else None
                price_pack = round(item["unit_price"] * units_per_pack * 0.95, 2) if units_per_pack > 1 else item["unit_price"]

                batch = models.InventoryBatch(
                    medicine_id=med.id,
                    batch_number=item["batch_no"],
                    expiry_date=date.today() + timedelta(days=item["exp_days"]),
                    stock_in_base_units=total_base_units,
                    cost_price_pack=item["package_cost"],
                    price_per_unit=item["unit_price"],
                    price_per_strip=price_strip,
                    price_per_pack=price_pack
                )
                db.add(batch)
                db.commit()
                db.refresh(batch)

                bin_entry = models.BinCardEntry(
                    batch_id=batch.id,
                    reference_doc=f"RCV-{item['batch_no']}",
                    movement_type="RECEIVED (IN)",
                    quantity_in=total_base_units,
                    quantity_out=0,
                    running_balance=total_base_units,
                    remarks=f"Initial Delivery ({item['packages_received']} pkgs)"
                )
                db.add(bin_entry)
                db.commit()
    except Exception as e:
        print(f"Catalog init log: {e}")
    finally:
        db.close()

seed_realistic_pharmacy_catalog()

app = FastAPI(title="Kush Drug Store POS Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = os.path.dirname(__file__)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
def serve_cashier_terminal():
    html_path = Path(__file__).resolve().parent / "cashier_terminal.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"), status_code=200)
    return HTMLResponse(content="<h2>cashier_terminal.html not found.</h2>", status_code=404)

# --- AUTHENTICATION ROUTES ---
class LoginPayload(BaseModel):
    pin: str

@app.post("/api/auth/login")
def authenticate_user(payload: LoginPayload):
    if payload.pin.strip() == ADMIN_MASTER_PIN:
        token = secrets.token_hex(16)
        ACTIVE_SESSIONS.add(token)
        return {"authenticated": True, "token": token}
    raise HTTPException(status_code=400, detail="Invalid Security Passcode / PIN")

@app.post("/api/auth/logout")
def logout_user(x_auth_token: Optional[str] = Header(None)):
    if x_auth_token in ACTIVE_SESSIONS:
        ACTIVE_SESSIONS.remove(x_auth_token)
    return {"message": "Logged out successfully"}

# --- INVENTORY & POS ROUTES ---
@app.get("/api/medicines")
def get_medicines_catalog(search: str = "", db: Session = Depends(get_database_session)):
    query = db.query(models.MedicineCatalog)
    if search:
        query = query.filter(
            (models.MedicineCatalog.brand_name.ilike(f"%{search}%")) |
            (models.MedicineCatalog.generic_name.ilike(f"%{search}%"))
        )
    medicines = query.all()
    out = []
    for m in medicines:
        batches_data = []
        for b in m.batches:
            batches_data.append({
                "id": b.id,
                "batch_number": b.batch_number,
                "expiry_date": b.expiry_date.strftime("%Y-%m-%d"),
                "stock_in_base_units": b.stock_in_base_units,
                "cost_price_pack": b.cost_price_pack,
                "price_per_unit": b.price_per_unit,
                "price_per_strip": b.price_per_strip,
                "price_per_pack": b.price_per_pack
            })
        out.append({
            "id": m.id,
            "brand_name": m.brand_name,
            "generic_name": m.generic_name,
            "dosage": m.dosage,
            "dosage_form": m.dosage_form,
            "dispense_unit": m.dispense_unit,
            "units_per_strip": m.units_per_strip,
            "strips_per_box": m.strips_per_box,
            "batches": batches_data
        })
    return out

class UniversalMedicineStockCreate(BaseModel):
    brand_name: str
    generic_name: Optional[str] = None
    dosage: Optional[str] = None
    dosage_form: str = "Tablet"
    dispense_unit: str = "Piece"
    units_per_subpack: int = Field(default=1, ge=1)
    subpacks_per_outerpack: int = Field(default=1, ge=1)
    batch_number: str
    expiry_date: date
    packages_received: int = Field(ge=1)
    cost_price_package: float = Field(ge=0)
    price_per_dispense_unit: float = Field(gt=0)
    price_per_strip: Optional[float] = None
    price_per_pack: Optional[float] = None

@app.post("/api/medicines/with-stock", status_code=status.HTTP_201_CREATED)
def create_universal_medicine_stock(
    data: UniversalMedicineStockCreate, 
    db: Session = Depends(get_database_session),
    auth: bool = Depends(verify_session_token)
):
    try:
        new_med = models.MedicineCatalog(
            brand_name=data.brand_name.strip(),
            generic_name=data.generic_name.strip() if data.generic_name else None,
            dosage=data.dosage.strip() if data.dosage else None,
            dosage_form=data.dosage_form,
            dispense_unit=data.dispense_unit,
            units_per_strip=data.units_per_subpack,
            strips_per_box=data.subpacks_per_outerpack
        )
        db.add(new_med)
        db.commit()
        db.refresh(new_med)

        units_per_pack = data.units_per_subpack * data.subpacks_per_outerpack
        total_base_units = data.packages_received * units_per_pack

        price_strip = data.price_per_strip or (
            round(data.price_per_dispense_unit * data.units_per_subpack, 2) if data.units_per_subpack > 1 else None
        )
        price_pack = data.price_per_pack or (
            round(data.price_per_dispense_unit * units_per_pack * 0.95, 2) if units_per_pack > 1 else data.price_per_dispense_unit
        )

        new_batch = models.InventoryBatch(
            medicine_id=new_med.id,
            batch_number=data.batch_number.strip(),
            expiry_date=data.expiry_date,
            stock_in_base_units=total_base_units,
            cost_price_pack=data.cost_price_package,
            price_per_unit=data.price_per_dispense_unit,
            price_per_strip=price_strip,
            price_per_pack=price_pack
        )
        db.add(new_batch)
        db.commit()
        db.refresh(new_batch)

        bin_in = models.BinCardEntry(
            batch_id=new_batch.id,
            reference_doc=f"RCV-{data.batch_number.strip()}",
            movement_type="RECEIVED (IN)",
            quantity_in=total_base_units,
            quantity_out=0,
            running_balance=total_base_units,
            remarks=f"Initial Delivery ({data.packages_received} pkgs)"
        )
        db.add(bin_in)
        db.commit()

        return {"message": "Product created successfully", "medicine_id": new_med.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")

class QuickRestockPayload(BaseModel):
    medicine_id: int
    batch_number: str
    expiry_date: date
    packages_received: int = Field(ge=1)
    cost_price_package: float = Field(ge=0)
    price_per_dispense_unit: Optional[float] = None
    remarks: Optional[str] = "Delivery Restock"

@app.post("/api/stock/restock", status_code=status.HTTP_201_CREATED)
def quick_restock_existing_medicine(
    data: QuickRestockPayload, 
    db: Session = Depends(get_database_session),
    auth: bool = Depends(verify_session_token)
):
    med = db.query(models.MedicineCatalog).filter(models.MedicineCatalog.id == data.medicine_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medicine not found in catalog")

    units_per_pack = med.units_per_strip * med.strips_per_box
    total_base_units = data.packages_received * units_per_pack

    existing_batch = db.query(models.InventoryBatch).filter(
        models.InventoryBatch.medicine_id == med.id,
        models.InventoryBatch.batch_number == data.batch_number.strip()
    ).first()

    if existing_batch:
        existing_batch.stock_in_base_units += total_base_units
        existing_batch.expiry_date = data.expiry_date
        existing_batch.cost_price_pack = data.cost_price_package
        if data.price_per_dispense_unit:
            existing_batch.price_per_unit = data.price_per_dispense_unit
            if med.units_per_strip > 1:
                existing_batch.price_per_strip = round(data.price_per_dispense_unit * med.units_per_strip, 2)
            existing_batch.price_per_pack = round(data.price_per_dispense_unit * units_per_pack * 0.95, 2)
        target_batch = existing_batch
    else:
        latest = med.batches[-1] if med.batches else None
        unit_p = data.price_per_dispense_unit or (latest.price_per_unit if latest else 1.0)
        p_strip = round(unit_p * med.units_per_strip, 2) if med.units_per_strip > 1 else None
        p_pack = round(unit_p * units_per_pack * 0.95, 2) if units_per_pack > 1 else unit_p

        new_batch = models.InventoryBatch(
            medicine_id=med.id,
            batch_number=data.batch_number.strip(),
            expiry_date=data.expiry_date,
            stock_in_base_units=total_base_units,
            cost_price_pack=data.cost_price_package,
            price_per_unit=unit_p,
            price_per_strip=p_strip,
            price_per_pack=p_pack
        )
        db.add(new_batch)
        db.commit()
        db.refresh(new_batch)
        target_batch = new_batch

    bin_in = models.BinCardEntry(
        batch_id=target_batch.id,
        reference_doc=f"RCV-{data.batch_number.strip()}",
        movement_type="RECEIVED (IN)",
        quantity_in=total_base_units,
        quantity_out=0,
        running_balance=target_batch.stock_in_base_units,
        remarks=f"{data.remarks} (+{data.packages_received} pkgs)"
    )
    db.add(bin_in)
    db.commit()

    return {"message": "Stock added successfully", "current_balance": target_batch.stock_in_base_units}

@app.delete("/api/batches/{batch_id}", status_code=status.HTTP_200_OK)
def delete_stock_batch(
    batch_id: int, 
    db: Session = Depends(get_database_session),
    auth: bool = Depends(verify_session_token)
):
    batch = db.query(models.InventoryBatch).filter(models.InventoryBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    med = batch.medicine
    
    db.query(models.BinCardEntry).filter(models.BinCardEntry.batch_id == batch_id).delete(synchronize_session=False)
    db.query(models.SalesTransactionItem).filter(models.SalesTransactionItem.batch_id == batch_id).delete(synchronize_session=False)

    db.delete(batch)
    db.commit()

    remaining_batches = db.query(models.InventoryBatch).filter(models.InventoryBatch.medicine_id == med.id).count()
    if remaining_batches == 0:
        db.delete(med)
        db.commit()

    return {"message": "Stock batch deleted successfully"}

class UpdatePricePayload(BaseModel):
    price_per_unit: float = Field(gt=0)
    price_per_strip: Optional[float] = None
    price_per_pack: Optional[float] = None

@app.put("/api/batches/{batch_id}/price")
def update_price_on_web(
    batch_id: int, 
    payload: UpdatePricePayload, 
    db: Session = Depends(get_database_session),
    auth: bool = Depends(verify_session_token)
):
    batch = db.query(models.InventoryBatch).filter(models.InventoryBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    batch.price_per_unit = payload.price_per_unit
    batch.price_per_strip = payload.price_per_strip
    batch.price_per_pack = payload.price_per_pack

    db.commit()
    return {"message": "Price updated successfully"}

class CartItemPayload(BaseModel):
    batch_id: int
    unit_type: str
    quantity: int = Field(ge=1)

class UniversalCheckoutRequest(BaseModel):
    payment_method: str = "Cash"
    notes: Optional[str] = None
    items: List[CartItemPayload]

@app.post("/api/checkout", status_code=status.HTTP_201_CREATED)
def process_universal_checkout(
    payload: UniversalCheckoutRequest, 
    db: Session = Depends(get_database_session),
    auth: bool = Depends(verify_session_token)
):
    if not payload.items:
        raise HTTPException(status_code=400, detail="Cart cannot be empty")

    total_bill = 0.0
    items_to_save = []
    invoice_id = f"KUSH-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    for item in payload.items:
        batch = db.query(models.InventoryBatch).filter(models.InventoryBatch.id == item.batch_id).first()
        if not batch:
            raise HTTPException(status_code=404, detail=f"Batch ID {item.batch_id} not found")

        med = batch.medicine
        units_per_pack = med.units_per_strip * med.strips_per_box

        unit = item.unit_type.lower()
        if unit in ["single", "unit", med.dispense_unit.lower()]:
            units_to_deduct = item.quantity
            price = batch.price_per_unit
            display_unit = med.dispense_unit
        elif unit in ["strip", "subpack"]:
            units_to_deduct = item.quantity * med.units_per_strip
            price = batch.price_per_strip or (batch.price_per_unit * med.units_per_strip)
            display_unit = "Strip/Subpack"
        elif unit in ["pack", "box", "carton"]:
            units_to_deduct = item.quantity * units_per_pack
            price = batch.price_per_pack or (batch.price_per_unit * units_per_pack)
            display_unit = "Outer Pack"
        else:
            units_to_deduct = item.quantity
            price = batch.price_per_unit
            display_unit = med.dispense_unit

        if batch.stock_in_base_units < units_to_deduct:
            raise HTTPException(
                status_code=400,
                detail=f"Low stock for {med.brand_name}. Needs {units_to_deduct} {med.dispense_unit}(s), only {batch.stock_in_base_units} available."
            )

        batch.stock_in_base_units -= units_to_deduct
        subtotal = round(price * item.quantity, 2)
        total_bill += subtotal

        items_to_save.append(
            models.SalesTransactionItem(
                batch_id=batch.id,
                unit_type=display_unit,
                quantity_dispensed=item.quantity,
                base_units_deducted=units_to_deduct,
                unit_price=price,
                line_subtotal=subtotal
            )
        )

        bin_out = models.BinCardEntry(
            batch_id=batch.id,
            reference_doc=invoice_id,
            movement_type="DISPENSED (OUT)",
            quantity_in=0,
            quantity_out=units_to_deduct,
            running_balance=batch.stock_in_base_units,
            remarks=f"Dispensed {item.quantity} {display_unit}(s)"
        )
        db.add(bin_out)

    sale_record = models.SalesTransaction(
        invoice_number=invoice_id,
        total_amount=round(total_bill, 2),
        payment_method=payload.payment_method,
        notes=payload.notes,
        items=items_to_save
    )
    db.add(sale_record)
    db.commit()
    db.refresh(sale_record)
    return {
        "invoice_number": sale_record.invoice_number,
        "total_amount": sale_record.total_amount,
        "payment_method": sale_record.payment_method,
        "notes": sale_record.notes
    }

@app.get("/api/stock/overview")
def get_stock_overview(db: Session = Depends(get_database_session)):
    batches = db.query(models.InventoryBatch).join(models.MedicineCatalog).all()
    today = date.today()
    stock_list = []

    for b in batches:
        med = b.medicine
        units_per_pack = med.units_per_strip * med.strips_per_box
        
        if units_per_pack > 1:
            packs = b.stock_in_base_units // units_per_pack
            rem = b.stock_in_base_units % units_per_pack
            if med.units_per_strip > 1:
                strips = rem // med.units_per_strip
                loose = rem % med.units_per_strip
                breakdown_str = f"{packs} packs, {strips} strips, {loose} {med.dispense_unit.lower()}s"
            else:
                breakdown_str = f"{packs} packs, {rem} {med.dispense_unit.lower()}s"
        else:
            breakdown_str = f"{b.stock_in_base_units} {med.dispense_unit.lower()}s"

        days_to_exp = (b.expiry_date - today).days
        if days_to_exp < 0:
            exp_status = "EXPIRED"
        elif days_to_exp <= 90:
            exp_status = "NEAR_EXPIRY"
        else:
            exp_status = "SAFE"

        stock_list.append({
            "batch_id": b.id,
            "medicine_id": med.id,
            "brand_name": med.brand_name,
            "generic_name": med.generic_name or "",
            "dosage": med.dosage or "",
            "dosage_form": med.dosage_form,
            "dispense_unit": med.dispense_unit,
            "units_per_strip": med.units_per_strip,
            "strips_per_box": med.strips_per_box,
            "batch_number": b.batch_number,
            "expiry_date": b.expiry_date.strftime("%Y-%m-%d"),
            "days_to_expiry": days_to_exp,
            "expiry_status": exp_status,
            "total_units": b.stock_in_base_units,
            "breakdown": breakdown_str,
            "price_per_unit": b.price_per_unit,
            "cost_price_pack": b.cost_price_pack
        })

    return stock_list

@app.get("/api/stock/bincard/{batch_id}")
def get_bincard_ledger(batch_id: int, db: Session = Depends(get_database_session)):
    batch = db.query(models.InventoryBatch).filter(models.InventoryBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    entries = db.query(models.BinCardEntry).filter(
        models.BinCardEntry.batch_id == batch_id
    ).order_by(models.BinCardEntry.entry_date.asc()).all()

    ledger = []
    for e in entries:
        ledger.append({
            "id": e.id,
            "date": e.entry_date.strftime("%Y-%m-%d %H:%M"),
            "reference_doc": e.reference_doc,
            "movement_type": e.movement_type,
            "quantity_in": e.quantity_in,
            "quantity_out": e.quantity_out,
            "running_balance": e.running_balance,
            "remarks": e.remarks or ""
        })

    return {
        "medicine_name": batch.medicine.brand_name,
        "dosage_form": batch.medicine.dosage_form,
        "dispense_unit": batch.medicine.dispense_unit,
        "batch_number": batch.batch_number,
        "expiry_date": batch.expiry_date.strftime("%Y-%m-%d"),
        "current_stock": batch.stock_in_base_units,
        "entries": ledger
    }

class StockAdjustmentRequest(BaseModel):
    batch_id: int
    adjustment_units: int = Field(gt=0)
    reason: str
    remarks: Optional[str] = None

@app.post("/api/stock/adjust", status_code=status.HTTP_200_OK)
def record_stock_adjustment(
    payload: StockAdjustmentRequest, 
    db: Session = Depends(get_database_session),
    auth: bool = Depends(verify_session_token)
):
    batch = db.query(models.InventoryBatch).filter(models.InventoryBatch.id == payload.batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    if batch.stock_in_base_units < payload.adjustment_units:
        raise HTTPException(status_code=400, detail="Cannot deduct more units than currently in stock")

    batch.stock_in_base_units -= payload.adjustment_units

    bin_entry = models.BinCardEntry(
        batch_id=batch.id,
        reference_doc=f"ADJ-{datetime.utcnow().strftime('%m%d')}-{payload.reason[:4].upper()}",
        movement_type=f"LOSS / {payload.reason.upper()}",
        quantity_in=0,
        quantity_out=payload.adjustment_units,
        running_balance=batch.stock_in_base_units,
        remarks=payload.remarks or payload.reason
    )
    db.add(bin_entry)
    db.commit()

    return {"message": "Stock adjusted and Bin Card updated", "new_balance": batch.stock_in_base_units}

@app.get("/api/sales/history")
def get_sales_history(target_date: Optional[str] = Query(None), db: Session = Depends(get_database_session)):
    sales = db.query(models.SalesTransaction).order_by(desc(models.SalesTransaction.created_at)).all()
    history = []
    
    for s in sales:
        if not s.created_at:
            continue
            
        sale_date_str = s.created_at.strftime("%Y-%m-%d")
        
        if target_date and target_date.strip() and sale_date_str != target_date.strip():
            continue

        item_details = []
        for i in s.items:
            med_name = i.batch.medicine.brand_name if i.batch and i.batch.medicine else "Medication"
            item_details.append(f"{med_name} ({i.quantity_dispensed} {i.unit_type})")
        
        history.append({
            "id": s.id,
            "invoice_number": s.invoice_number,
            "created_at": s.created_at.strftime("%Y-%m-%d %H:%M"),
            "total_amount": float(s.total_amount),
            "payment_method": s.payment_method,
            "summary_items": ", ".join(item_details),
            "notes": s.notes or ""
        })
    return history

@app.get("/api/sales/summary")
def get_sales_summary(target_date: Optional[str] = Query(None), db: Session = Depends(get_database_session)):
    sales = db.query(models.SalesTransaction).all()
    check_date = target_date.strip() if (target_date and target_date.strip()) else date.today().strftime("%Y-%m-%d")
    
    filtered_sales = []
    for s in sales:
        if s.created_at and s.created_at.strftime("%Y-%m-%d") == check_date:
            filtered_sales.append(s)

    total_revenue = sum(s.total_amount for s in filtered_sales)
    cash_total = sum(s.total_amount for s in filtered_sales if s.payment_method == "Cash")
    telebirr_total = sum(s.total_amount for s in filtered_sales if "Telebirr" in s.payment_method)
    cbe_total = sum(s.total_amount for s in filtered_sales if "CBE" in s.payment_method)

    return {
        "total_revenue": round(total_revenue, 2),
        "total_orders": len(filtered_sales),
        "cash_total": round(cash_total, 2),
        "telebirr_total": round(telebirr_total, 2),
        "cbe_total": round(cbe_total, 2)
    }