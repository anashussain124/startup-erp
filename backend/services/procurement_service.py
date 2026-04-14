"""
Procurement Service — business logic for Vendor, PurchaseOrder, InventoryItem.
"""
from sqlalchemy.orm import Session
from models.procurement import Vendor, PurchaseOrder, InventoryItem
from schemas.procurement import (
    VendorCreate, VendorUpdate,
    PurchaseOrderCreate, PurchaseOrderUpdate,
    InventoryItemCreate, InventoryItemUpdate,
)


# ═══════════════════════════════════════════════════════════════════════════
# Vendor CRUD
# ═══════════════════════════════════════════════════════════════════════════
def create_vendor(db: Session, data: VendorCreate) -> Vendor:
    vendor = Vendor(**data.model_dump())
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor


def get_vendors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Vendor).offset(skip).limit(limit).all()


def get_vendor(db: Session, vendor_id: int) -> Vendor | None:
    return db.query(Vendor).filter(Vendor.id == vendor_id).first()


def update_vendor(db: Session, vendor_id: int, data: VendorUpdate) -> Vendor | None:
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(vendor, key, value)
    db.commit()
    db.refresh(vendor)
    return vendor


def delete_vendor(db: Session, vendor_id: int) -> bool:
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        return False
    db.delete(vendor)
    db.commit()
    return True


# ═══════════════════════════════════════════════════════════════════════════
# PurchaseOrder CRUD
# ═══════════════════════════════════════════════════════════════════════════
def create_purchase_order(db: Session, data: PurchaseOrderCreate) -> PurchaseOrder:
    po = PurchaseOrder(**data.model_dump())
    db.add(po)
    db.commit()
    db.refresh(po)
    return po


def get_purchase_orders(db: Session, skip: int = 0, limit: int = 100, status: str | None = None):
    q = db.query(PurchaseOrder)
    if status:
        q = q.filter(PurchaseOrder.status == status)
    return q.order_by(PurchaseOrder.order_date.desc()).offset(skip).limit(limit).all()


def get_purchase_order(db: Session, po_id: int) -> PurchaseOrder | None:
    return db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()


def update_purchase_order(db: Session, po_id: int, data: PurchaseOrderUpdate) -> PurchaseOrder | None:
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(po, key, value)
    db.commit()
    db.refresh(po)
    return po


def delete_purchase_order(db: Session, po_id: int) -> bool:
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        return False
    db.delete(po)
    db.commit()
    return True


# ═══════════════════════════════════════════════════════════════════════════
# InventoryItem CRUD
# ═══════════════════════════════════════════════════════════════════════════
def create_inventory_item(db: Session, data: InventoryItemCreate) -> InventoryItem:
    item = InventoryItem(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_inventory_items(db: Session, skip: int = 0, limit: int = 100, low_stock: bool = False):
    q = db.query(InventoryItem)
    if low_stock:
        q = q.filter(InventoryItem.quantity <= InventoryItem.reorder_level)
    return q.offset(skip).limit(limit).all()


def get_inventory_item(db: Session, item_id: int) -> InventoryItem | None:
    return db.query(InventoryItem).filter(InventoryItem.id == item_id).first()


def update_inventory_item(db: Session, item_id: int, data: InventoryItemUpdate) -> InventoryItem | None:
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


def delete_inventory_item(db: Session, item_id: int) -> bool:
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True
