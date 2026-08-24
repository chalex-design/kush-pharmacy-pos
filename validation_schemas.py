from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field

# --- Medicine Validation ---
class MedicineSchemaCreate(BaseModel):
    brand_name: str
    generic_name: Optional[str] = None
    dosage: Optional[str] = None
    dosage_form: str = "Tablet"
    units_per_strip: int = 10
    strips_per_box: int = 10

class BatchSchemaOut(BaseModel):
    id: int
    medicine_id: int
    batch_number: str
    expiry_date: date
    stock_in_tablets: int
    price_per_tablet: float
    price_per_strip: Optional[float]
    price_per_box: Optional[float]

    class Config:
        from_attributes = True

class MedicineSchemaOut(MedicineSchemaCreate):
    id: int
    created_at: datetime
    batches: List[BatchSchemaOut] = []

    class Config:
        from_attributes = True

# --- Batch Creation ---
class BatchSchemaCreate(BaseModel):
    medicine_id: int
    batch_number: str
    expiry_date: date
    boxes_received: int = Field(ge=0)
    cost_price_box: float = Field(gt=0)
    price_per_tablet: float = Field(gt=0)
    price_per_strip: Optional[float] = None
    price_per_box: Optional[float] = None

# --- Checkout / Sales Validation ---
class SaleItemRequest(BaseModel):
    batch_id: int
    unit_type: str = "tablet"                                      # "tablet", "strip", or "box"
    quantity: int = Field(gt=0)

class SaleCheckoutRequest(BaseModel):
    payment_method: str = "Cash"
    notes: Optional[str] = None
    items: List[SaleItemRequest]

class SaleItemResponse(BaseModel):
    id: int
    batch_id: int
    unit_type: str
    quantity_dispensed: int
    unit_price: float
    line_subtotal: float

    class Config:
        from_attributes = True

class SaleCheckoutResponse(BaseModel):
    id: int
    invoice_number: str
    created_at: datetime
    total_amount: float
    payment_method: str
    items: List[SaleItemResponse]

    class Config:
        from_attributes = True