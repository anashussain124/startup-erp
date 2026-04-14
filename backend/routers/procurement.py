"""
Procurement Router — Vendor, PurchaseOrder, InventoryItem endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user, require_role
from schemas.procurement import (
    VendorCreate, VendorUpdate, VendorOut,
    PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderOut,
    InventoryItemCreate, InventoryItemUpdate, InventoryItemOut,
)
from services import procurement_service

router = APIRouter(prefix="/api", tags=["Procurement"])


# ── Vendors ──────────────────────────────────────────────────────────────────
@router.post("/vendors", response_model=VendorOut, status_code=201)
def create_vendor(
    data: VendorCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "manager")),
):
    return procurement_service.create_vendor(db, data)


@router.get("/vendors", response_model=list[VendorOut])
def list_vendors(
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return procurement_service.get_vendors(db, skip, limit)


@router.get("/vendors/{vendor_id}", response_model=VendorOut)
def get_vendor(vendor_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    vendor = procurement_service.get_vendor(db, vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor


@router.put("/vendors/{vendor_id}", response_model=VendorOut)
def update_vendor(
    vendor_id: int,
    data: VendorUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "manager")),
):
    vendor = procurement_service.update_vendor(db, vendor_id, data)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor


@router.delete("/vendors/{vendor_id}", status_code=204)
def delete_vendor(
    vendor_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin")),
):
    if not procurement_service.delete_vendor(db, vendor_id):
        raise HTTPException(status_code=404, detail="Vendor not found")


# ── Purchase Orders ──────────────────────────────────────────────────────────
@router.post("/purchase-orders", response_model=PurchaseOrderOut, status_code=201)
def create_purchase_order(
    data: PurchaseOrderCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "manager")),
):
    return procurement_service.create_purchase_order(db, data)


@router.get("/purchase-orders", response_model=list[PurchaseOrderOut])
def list_purchase_orders(
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    status: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return procurement_service.get_purchase_orders(db, skip, limit, status)


@router.get("/purchase-orders/{po_id}", response_model=PurchaseOrderOut)
def get_purchase_order(po_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    po = procurement_service.get_purchase_order(db, po_id)
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return po


@router.put("/purchase-orders/{po_id}", response_model=PurchaseOrderOut)
def update_purchase_order(
    po_id: int,
    data: PurchaseOrderUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "manager")),
):
    po = procurement_service.update_purchase_order(db, po_id, data)
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return po


@router.delete("/purchase-orders/{po_id}", status_code=204)
def delete_purchase_order(
    po_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin")),
):
    if not procurement_service.delete_purchase_order(db, po_id):
        raise HTTPException(status_code=404, detail="Purchase order not found")


# ── Inventory ────────────────────────────────────────────────────────────────
@router.post("/inventory", response_model=InventoryItemOut, status_code=201)
def create_inventory_item(
    data: InventoryItemCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "manager")),
):
    return procurement_service.create_inventory_item(db, data)


@router.get("/inventory", response_model=list[InventoryItemOut])
def list_inventory(
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    low_stock: bool = False,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return procurement_service.get_inventory_items(db, skip, limit, low_stock)


@router.get("/inventory/{item_id}", response_model=InventoryItemOut)
def get_inventory_item(item_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    item = procurement_service.get_inventory_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.put("/inventory/{item_id}", response_model=InventoryItemOut)
def update_inventory_item(
    item_id: int,
    data: InventoryItemUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "manager")),
):
    item = procurement_service.update_inventory_item(db, item_id, data)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.delete("/inventory/{item_id}", status_code=204)
def delete_inventory_item(
    item_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin")),
):
    if not procurement_service.delete_inventory_item(db, item_id):
        raise HTTPException(status_code=404, detail="Item not found")
