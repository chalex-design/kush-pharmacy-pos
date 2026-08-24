from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from config_database import Base

class MedicineCatalog(Base):
    __tablename__ = "medicine_catalog"

    id = Column(Integer, primary_key=True, index=True)
    brand_name = Column(String(100), nullable=False, index=True)
    generic_name = Column(String(100), nullable=True, index=True)
    dosage = Column(String(50), nullable=True)
    dosage_form = Column(String(50), default="Tablet")
    dispense_unit = Column(String(30), default="Piece")
    units_per_strip = Column(Integer, default=1)
    strips_per_box = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    batches = relationship("InventoryBatch", back_populates="medicine", cascade="all, delete-orphan")

class InventoryBatch(Base):
    __tablename__ = "inventory_batches"

    id = Column(Integer, primary_key=True, index=True)
    medicine_id = Column(Integer, ForeignKey("medicine_catalog.id"), nullable=False)
    batch_number = Column(String(50), nullable=False, index=True)
    expiry_date = Column(Date, nullable=False, index=True)
    stock_in_base_units = Column(Integer, nullable=False, default=0)
    cost_price_pack = Column(Float, nullable=False, default=0.0)
    price_per_unit = Column(Float, nullable=False)
    price_per_strip = Column(Float, nullable=True)
    price_per_pack = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    medicine = relationship("MedicineCatalog", back_populates="batches")
    sales_items = relationship("SalesTransactionItem", back_populates="batch")
    bin_card_entries = relationship("BinCardEntry", back_populates="batch", cascade="all, delete-orphan")

class BinCardEntry(Base):
    __tablename__ = "bin_card_entries"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("inventory_batches.id"), nullable=False)
    entry_date = Column(DateTime, default=datetime.utcnow, index=True)
    reference_doc = Column(String(100), nullable=False)
    movement_type = Column(String(50), nullable=False)
    quantity_in = Column(Integer, default=0)
    quantity_out = Column(Integer, default=0)
    running_balance = Column(Integer, nullable=False)
    remarks = Column(String(255), nullable=True)

    batch = relationship("InventoryBatch", back_populates="bin_card_entries")

class SalesTransaction(Base):
    __tablename__ = "sales_transactions"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    total_amount = Column(Float, nullable=False)
    payment_method = Column(String(50), default="Cash")
    notes = Column(Text, nullable=True)

    items = relationship("SalesTransactionItem", back_populates="transaction", cascade="all, delete-orphan")

class SalesTransactionItem(Base):
    __tablename__ = "sales_transaction_items"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("sales_transactions.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("inventory_batches.id"), nullable=False)
    unit_type = Column(String(30), nullable=False)
    quantity_dispensed = Column(Integer, nullable=False)
    base_units_deducted = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    line_subtotal = Column(Float, nullable=False)

    transaction = relationship("SalesTransaction", back_populates="items")
    batch = relationship("InventoryBatch", back_populates="sales_items")