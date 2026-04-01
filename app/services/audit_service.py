"""
Audit Service - Tracks user actions across the application.
"""
import json
from flask import request
from app.extensions import db
from app.models.audit import AuditLog


class AuditService:
    """Audit logging for all business operations."""

    @staticmethod
    def log(user_id, action, entity_type=None, entity_id=None,
            description=None, company_id=None, old_values=None, new_values=None):
        """
        Create an audit log entry.
        """
        log = AuditLog(
            company_id=company_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            ip_address=request.remote_addr if request else None,
            user_agent=str(request.user_agent) if request else None,
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None,
        )
        db.session.add(log)
        # Don't commit here - let the caller manage the transaction
        return log

    @staticmethod
    def get_logs(company_id=None, user_id=None, entity_type=None,
                 page=1, per_page=50):
        """Retrieve audit logs with filtering."""
        query = AuditLog.query

        if company_id:
            query = query.filter_by(company_id=company_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        if entity_type:
            query = query.filter_by(entity_type=entity_type)

        query = query.order_by(AuditLog.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)
