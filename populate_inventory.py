from datetime import date, timedelta
from config_database import SessionLocal, Base, engine
import inventory_models as models

print("--- Starting Standard Inventory Seeding for Kush Drug Store ---")

# Ensure database tables exist
Base.metadata.create_all(bind=engine)
db = SessionLocal()

# Standard Community Pharmacy Medicines Catalog
standard_catalog = [
    # --- Antibiotics & Anti-Infectives ---
    {
        "brand_name": "Amoxil", "generic_name": "Amoxicillin", "dosage": "500mg",
        "dosage_form": "Capsule", "units_per_strip": 10, "strips_per_box": 10,
        "batch_no": "AMX-801", "exp_days": 450, "boxes": 10, "box_cost": 220.0, "tab_price": 3.00
    },
    {
        "brand_name": "Augmentin", "generic_name": "Amoxicillin + Clavulanic Acid", "dosage": "625mg",
        "dosage_form": "Tablet", "units_per_strip": 7, "strips_per_box": 2,
        "batch_no": "AUG-302", "exp_days": 380, "boxes": 8, "box_cost": 280.0, "tab_price": 25.00
    },
    {
        "brand_name": "Cipro", "generic_name": "Ciprofloxacin", "dosage": "500mg",
        "dosage_form": "Tablet", "units_per_strip": 10, "strips_per_box": 2,
        "batch_no": "CPR-104", "exp_days": 360, "boxes": 12, "box_cost": 85.0, "tab_price": 5.50
    },
    {
        "brand_name": "Azithromycin", "generic_name": "Azithromycin", "dosage": "500mg",
        "dosage_form": "Tablet", "units_per_strip": 3, "strips_per_box": 1,
        "batch_no": "AZT-091", "exp_days": 500, "boxes": 20, "box_cost": 45.0, "tab_price": 18.00
    },
    {
        "brand_name": "Flagyl", "generic_name": "Metronidazole", "dosage": "250mg",
        "dosage_form": "Tablet", "units_per_strip": 10, "strips_per_box": 10,
        "batch_no": "FLG-512", "exp_days": 600, "boxes": 6, "box_cost": 110.0, "tab_price": 1.75
    },
    {
        "brand_name": "Doxycycline", "generic_name": "Doxycycline Hyclate", "dosage": "100mg",
        "dosage_form": "Capsule", "units_per_strip": 10, "strips_per_box": 10,
        "batch_no": "DOX-774", "exp_days": 400, "boxes": 5, "box_cost": 130.0, "tab_price": 2.00
    },

    # --- Analgesics, Antipyretics & NSAIDs ---
    {
        "brand_name": "Panadol Extra", "generic_name": "Paracetamol + Caffeine", "dosage": "500mg/65mg",
        "dosage_form": "Tablet", "units_per_strip": 12, "strips_per_box": 8,
        "batch_no": "PAN-921", "exp_days": 650, "boxes": 15, "box_cost": 95.0, "tab_price": 1.50
    },
    {
        "brand_name": "Brufen", "generic_name": "Ibuprofen", "dosage": "400mg",
        "dosage_form": "Tablet", "units_per_strip": 10, "strips_per_box": 10,
        "batch_no": "BRU-440", "exp_days": 520, "boxes": 10, "box_cost": 140.0, "tab_price": 2.00
    },
    {
        "brand_name": "Voltaren", "generic_name": "Diclofenac Sodium", "dosage": "50mg",
        "dosage_form": "Tablet", "units_per_strip": 10, "strips_per_box": 10,
        "batch_no": "VLT-118", "exp_days": 480, "boxes": 8, "box_cost": 160.0, "tab_price": 2.50
    },
    {
        "brand_name": "Tramadol", "generic_name": "Tramadol Hydrochloride", "dosage": "50mg",
        "dosage_form": "Capsule", "units_per_strip": 10, "strips_per_box": 10,
        "batch_no": "TRM-603", "exp_days": 350, "boxes": 4, "box_cost": 210.0, "tab_price": 3.50
    },

    # --- Gastrointestinal & Antacids ---
    {
        "brand_name": "Omeprazole", "generic_name": "Omeprazole", "dosage": "20mg",
        "dosage_form": "Capsule", "units_per_strip": 14, "strips_per_box": 2,
        "batch_no": "OMP-882", "exp_days": 420, "boxes": 12, "box_cost": 75.0, "tab_price": 3.50
    },
    {
        "brand_name": "Cimetidine", "generic_name": "Cimetidine", "dosage": "400mg",
        "dosage_form": "Tablet", "units_per_strip": 10, "strips_per_box": 10,
        "batch_no": "CMT-209", "exp_days": 510, "boxes": 6, "box_cost": 120.0, "tab_price": 1.80
    },

    # --- Cardiovascular & Antihypertensives ---
    {
        "brand_name": "Amlodipine", "generic_name": "Amlodipine Besylate", "dosage": "5mg",
        "dosage_form": "Tablet", "units_per_strip": 10, "strips_per_box": 3,
        "batch_no": "AML-315", "exp_days": 460, "boxes": 10, "box_cost": 60.0, "tab_price": 2.50
    },
    {
        "brand_name": "Enalapril", "generic_name": "Enalapril Maleate", "dosage": "10mg",
        "dosage_form": "Tablet", "units_per_strip": 10, "strips_per_box": 3,
        "batch_no": "ENL-404", "exp_days": 540, "boxes": 10, "box_cost": 65.0, "tab_price": 2.80
    },
    {
        "brand_name": "Atenolol", "generic_name": "Atenolol", "dosage": "50mg",
        "dosage_form": "Tablet", "units_per_strip": 14, "strips_per_box": 2,
        "batch_no": "ATN-711", "exp_days": 490, "boxes": 8, "box_cost": 70.0, "tab_price": 3.00
    },

    # --- Antidiabetic ---
    {
        "brand_name": "Metformin", "generic_name": "Metformin Hydrochloride", "dosage": "500mg",
        "dosage_form": "Tablet", "units_per_strip": 10, "strips_per_box": 10,
        "batch_no": "MTF-501", "exp_days": 550, "boxes": 10, "box_cost": 150.0, "tab_price": 2.00
    },
    {
        "brand_name": "Glibenclamide", "generic_name": "Glibenclamide", "dosage": "5mg",
        "dosage_form": "Tablet", "units_per_strip": 10, "strips_per_box": 10,
        "batch_no": "GLB-108", "exp_days": 600, "boxes": 5, "box_cost": 110.0, "tab_price": 1.50
    },

    # --- Antihistamines & Cold Relief ---
    {
        "brand_name": "Cetirizine", "generic_name": "Cetirizine Hydrochloride", "dosage": "10mg",
        "dosage_form": "Tablet", "units_per_strip": 10, "strips_per_box": 10,
        "batch_no": "CTZ-221", "exp_days": 620, "boxes": 8, "box_cost": 90.0, "tab_price": 1.50
    },
    {
        "brand_name": "Chlorpheniramine", "generic_name": "Chlorpheniramine Maleate", "dosage": "4mg",
        "dosage_form": "Tablet", "units_per_strip": 10, "strips_per_box": 100,
        "batch_no": "CPM-005", "exp_days": 700, "boxes": 2, "box_cost": 250.0, "tab_price": 0.50
    },

    # --- Vitamins & Minerals ---
    {
        "brand_name": "Vitamin C", "generic_name": "Ascorbic Acid", "dosage": "500mg",
        "dosage_form": "Tablet", "units_per_strip": 10, "strips_per_box": 10,
        "batch_no": "VTC-990", "exp_days": 580, "boxes": 12, "box_cost": 100.0, "tab_price": 1.50
    },
    {
        "brand_name": "Vitamin B Complex", "generic_name": "B1 + B6 + B12", "dosage": "High Potency",
        "dosage_form": "Tablet", "units_per_strip": 10, "strips_per_box": 10,
        "batch_no": "VTB-331", "exp_days": 500, "boxes": 10, "box_cost": 120.0, "tab_price": 1.80
    }
]

try:
    for item in standard_catalog:
        existing = db.query(models.MedicineCatalog).filter(
            models.MedicineCatalog.brand_name == item["brand_name"]
        ).first()

        if not existing:
            med = models.MedicineCatalog(
                brand_name=item["brand_name"],
                generic_name=item["generic_name"],
                dosage=item["dosage"],
                dosage_form=item["dosage_form"],
                units_per_strip=item["units_per_strip"],
                strips_per_box=item["strips_per_box"]
            )
            db.add(med)
            db.commit()
            db.refresh(med)

            tablets_total = item["boxes"] * (item["units_per_strip"] * item["strips_per_box"])
            batch = models.InventoryBatch(
                medicine_id=med.id,
                batch_number=item["batch_no"],
                expiry_date=date.today() + timedelta(days=item["exp_days"]),
                stock_in_tablets=tablets_total,
                cost_price_box=item["box_cost"],
                price_per_tablet=item["tab_price"],
                price_per_strip=round(item["tab_price"] * item["units_per_strip"] * 0.95, 2),
                price_per_box=round(item["tab_price"] * item["units_per_strip"] * item["strips_per_box"] * 0.90, 2)
            )
            db.add(batch)
            db.commit()
            db.refresh(batch)

            # Record initial Bin Card IN ledger
            bin_entry = models.BinCardEntry(
                batch_id=batch.id,
                reference_doc=f"RCV-{item['batch_no']}",
                movement_type="RECEIVED (IN)",
                quantity_in=tablets_total,
                quantity_out=0,
                running_balance=tablets_total,
                remarks=f"Initial Delivery ({item['boxes']} boxes)"
            )
            db.add(bin_entry)
            db.commit()

            print(f"Added: {item['brand_name']} ({tablets_total} tablets in stock)")
        else:
            print(f"Already in database: {item['brand_name']}")

    print("\n--- Standard Inventory Seeded Successfully! ---")
except Exception as e:
    print(f"\nError occurred: {e}")
finally:
    db.close()