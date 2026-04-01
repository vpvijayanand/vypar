"""
Inventory Service - Stock management business logic.
Handles stock updates, low stock alerts, and stock valuation.
"""
from decimal import Decimal
from app.extensions import db
from app.models.item import Item
from app.models.stock import StockLog


class InventoryService:
    """Business logic for inventory/stock management."""

    @staticmethod
    def update_stock(company_id, item_id, quantity_change, transaction_type,
                     reference_type=None, reference_id=None, unit_cost=0,
                     notes=None, user_id=None):
        """
        Update stock for an item and log the movement.

        Args:
            company_id: company context
            item_id: item to update
            quantity_change: positive = stock in, negative = stock out
            transaction_type: sale, purchase, sale_return, purchase_return, adjustment
            reference_type: invoice, bill, return, manual
            reference_id: ID of the reference document
            unit_cost: cost per unit for this transaction
            user_id: user performing the action

        Returns: StockLog entry
        """
        item = Item.query.filter_by(id=item_id, company_id=company_id).first()
        if not item:
            raise ValueError(f"Item {item_id} not found for company {company_id}")

        qty_before = float(item.current_stock or 0)
        qty_after = qty_before + float(quantity_change)

        if qty_after < 0:
            raise ValueError(
                f"Insufficient stock for {item.item_name}. "
                f"Available: {qty_before}, Requested: {abs(float(quantity_change))}"
            )

        # Update item stock
        item.current_stock = Decimal(str(qty_after))

        # Create stock log
        log = StockLog(
            company_id=company_id,
            item_id=item_id,
            transaction_type=transaction_type,
            reference_type=reference_type,
            reference_id=reference_id,
            quantity_change=Decimal(str(quantity_change)),
            quantity_before=Decimal(str(qty_before)),
            quantity_after=Decimal(str(qty_after)),
            unit_cost=Decimal(str(unit_cost)),
            notes=notes,
            created_by=user_id,
        )
        db.session.add(log)
        return log

    @staticmethod
    def process_sale_stock(company_id, invoice_items, user_id=None):
        """
        Reduce stock for all items in a sale invoice.

        Args:
            company_id: company context
            invoice_items: list of dicts with item_id, quantity, unit_price
            user_id: user performing the action
        """
        for item_data in invoice_items:
            InventoryService.update_stock(
                company_id=company_id,
                item_id=item_data['item_id'],
                quantity_change=-abs(float(item_data['quantity'])),
                transaction_type='sale',
                reference_type='invoice',
                reference_id=item_data.get('invoice_id'),
                unit_cost=float(item_data.get('unit_price', 0)),
                user_id=user_id,
            )

    @staticmethod
    def process_purchase_stock(company_id, bill_items, user_id=None):
        """
        Increase stock for all items in a purchase bill.
        """
        for item_data in bill_items:
            InventoryService.update_stock(
                company_id=company_id,
                item_id=item_data['item_id'],
                quantity_change=abs(float(item_data['quantity'])),
                transaction_type='purchase',
                reference_type='bill',
                reference_id=item_data.get('bill_id'),
                unit_cost=float(item_data.get('unit_price', 0)),
                user_id=user_id,
            )

    @staticmethod
    def process_sale_return_stock(company_id, return_items, user_id=None):
        """Add stock back for sale returns."""
        for item_data in return_items:
            InventoryService.update_stock(
                company_id=company_id,
                item_id=item_data['item_id'],
                quantity_change=abs(float(item_data['quantity'])),
                transaction_type='sale_return',
                reference_type='return',
                reference_id=item_data.get('return_id'),
                unit_cost=float(item_data.get('unit_price', 0)),
                user_id=user_id,
            )

    @staticmethod
    def process_purchase_return_stock(company_id, return_items, user_id=None):
        """Reduce stock for purchase returns."""
        for item_data in return_items:
            InventoryService.update_stock(
                company_id=company_id,
                item_id=item_data['item_id'],
                quantity_change=-abs(float(item_data['quantity'])),
                transaction_type='purchase_return',
                reference_type='return',
                reference_id=item_data.get('return_id'),
                unit_cost=float(item_data.get('unit_price', 0)),
                user_id=user_id,
            )

    @staticmethod
    def get_low_stock_items(company_id):
        """Get all items where current_stock <= min_stock_alert."""
        return Item.query.filter(
            Item.company_id == company_id,
            Item.is_active == True,
            Item.current_stock <= Item.min_stock_alert
        ).all()

    @staticmethod
    def get_stock_value(company_id):
        """Calculate total stock value for a company."""
        items = Item.query.filter_by(company_id=company_id, is_active=True).all()
        return sum(item.stock_value for item in items)

    @staticmethod
    def get_stock_summary(company_id):
        """Get stock summary with counts and value."""
        items = Item.query.filter_by(company_id=company_id, is_active=True).all()
        total_items = len(items)
        low_stock = sum(1 for item in items if item.is_low_stock)
        out_of_stock = sum(1 for item in items if float(item.current_stock or 0) <= 0)
        total_value = sum(item.stock_value for item in items)

        return {
            'total_items': total_items,
            'low_stock_count': low_stock,
            'out_of_stock_count': out_of_stock,
            'total_stock_value': round(total_value, 2),
        }
