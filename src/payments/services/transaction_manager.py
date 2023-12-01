"""
Transaction manager for coordinating payment operations.

This module provides transaction management capabilities for ensuring
data consistency across payment operations.
"""

import logging
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Generator, Optional
import uuid

from payments.logging_config import get_logger
from payments.models.transaction import Transaction, TransactionLog, TransactionType

logger = get_logger(__name__)


class TransactionState(str, Enum):
    """Transaction state for the manager."""
    IDLE = "idle"
    ACTIVE = "active"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"


@dataclass
class TransactionContext:
    """Context for an active transaction."""
    
    id: str
    state: TransactionState
    started_at: datetime
    operations: list[dict[str, Any]]
    
    @classmethod
    def create(cls) -> "TransactionContext":
        """Create a new transaction context."""
        return cls(
            id=f"txn_ctx_{uuid.uuid4().hex[:12]}",
            state=TransactionState.ACTIVE,
            started_at=datetime.utcnow(),
            operations=[],
        )


class TransactionManager:
    """
    Manages transactions for payment operations.
    
    Provides begin/commit/rollback semantics for coordinating
    multiple operations atomically.
    
    TODO(TEAM-PAYMENTS): Integrate with real database transactions.
    """
    
    def __init__(self):
        self._current_transaction: Optional[TransactionContext] = None
        self._transaction_logs: list[TransactionLog] = []
    
    @property
    def in_transaction(self) -> bool:
        """Check if a transaction is active."""
        return (
            self._current_transaction is not None
            and self._current_transaction.state == TransactionState.ACTIVE
        )
    
    def begin(self) -> TransactionContext:
        """
        Begin a new transaction.
        
        Raises if a transaction is already active.
        """
        if self.in_transaction:
            raise RuntimeError("Transaction already in progress")
        
        self._current_transaction = TransactionContext.create()
        
        logger.info(
            "Transaction started",
            extra={"transaction_id": self._current_transaction.id},
        )
        
        return self._current_transaction
    
    def commit(self) -> None:
        """
        Commit the current transaction.
        
        Raises if no transaction is active.
        """
        if not self.in_transaction:
            raise RuntimeError("No active transaction to commit")
        
        assert self._current_transaction is not None
        
        self._current_transaction.state = TransactionState.COMMITTED
        
        # Log commit
        self._log_event(self._current_transaction.id, "COMMITTED", {
            "operations_count": len(self._current_transaction.operations),
        })
        
        logger.info(
            "Transaction committed",
            extra={
                "transaction_id": self._current_transaction.id,
                "operations": len(self._current_transaction.operations),
            },
        )
        
        self._current_transaction = None
    
    def rollback(self, reason: Optional[str] = None) -> None:
        """
        Rollback the current transaction.
        
        Raises if no transaction is active.
        """
        if not self.in_transaction:
            raise RuntimeError("No active transaction to rollback")
        
        assert self._current_transaction is not None
        
        self._current_transaction.state = TransactionState.ROLLED_BACK
        
        # Log rollback
        self._log_event(self._current_transaction.id, "ROLLED_BACK", {
            "reason": reason,
            "operations_count": len(self._current_transaction.operations),
        })
        
        logger.warning(
            "Transaction rolled back",
            extra={
                "transaction_id": self._current_transaction.id,
                "reason": reason,
                "operations": len(self._current_transaction.operations),
            },
        )
        
        self._current_transaction = None
    
    def record_operation(
        self,
        operation_type: str,
        data: dict[str, Any],
    ) -> None:
        """Record an operation within the current transaction."""
        if not self.in_transaction:
            # Log but don't fail for operations outside transactions
            logger.warning(
                "Operation recorded outside transaction",
                extra={"operation_type": operation_type},
            )
            return
        
        assert self._current_transaction is not None
        
        self._current_transaction.operations.append({
            "type": operation_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        })
    
    @contextmanager
    def transaction(self) -> Generator[TransactionContext, None, None]:
        """
        Context manager for transactions.
        
        Automatically commits on success or rolls back on exception.
        
        Usage:
            with transaction_manager.transaction() as txn:
                # perform operations
                pass
        """
        ctx = self.begin()
        try:
            yield ctx
            self.commit()
        except Exception as e:
            self.rollback(reason=str(e))
            raise
    
    def _log_event(
        self,
        transaction_id: str,
        event: str,
        data: dict[str, Any],
    ) -> None:
        """Log a transaction event."""
        log = TransactionLog.log_event(transaction_id, event, data)
        self._transaction_logs.append(log)


class LegacyTransactionManager:
    """
    Legacy transaction manager for backward compatibility.
    
    TODO(TEAM-PAYMENTS): Remove after v1 API deprecation.
    
    This class uses synchronous methods and older patterns.
    """
    
    def __init__(self):
        self._active = False
    
    def start_transaction(self) -> str:
        """
        Start a transaction synchronously.
        
        TODO(TEAM-PAYMENTS): Migrate to async TransactionManager.
        """
        # Legacy logging pattern
        logging.info("Starting legacy transaction")
        
        self._active = True
        return f"legacy_txn_{uuid.uuid4().hex[:8]}"
    
    def commit_transaction(self, transaction_id: str) -> bool:
        """
        Commit a transaction synchronously.
        
        TODO(TEAM-PAYMENTS): Migrate to async TransactionManager.
        """
        logging.info("Committing legacy transaction: %s", transaction_id)
        
        self._active = False
        return True
    
    def rollback_transaction(self, transaction_id: str) -> bool:
        """
        Rollback a transaction synchronously.
        
        TODO(TEAM-PAYMENTS): Migrate to async TransactionManager.
        """
        logging.info("Rolling back legacy transaction: %s", transaction_id)
        
        self._active = False
        return True
