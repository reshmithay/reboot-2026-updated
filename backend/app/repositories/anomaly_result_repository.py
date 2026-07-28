"""
Anomaly Results repository for PostgreSQL.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.anomaly_result import AnomalyResult
from app.utilities.logger.logger import get_logger

logger = get_logger(__name__)


class AnomalyResultRepository:
    """PostgreSQL repository for anomaly results operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, anomaly_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new anomaly result record."""
        try:
            anomaly = AnomalyResult(**anomaly_data)
            self.session.add(anomaly)
            await self.session.flush()
            await self.session.refresh(anomaly)
            
            logger.info(f"Created anomaly result {anomaly.anomaly_id} in PostgreSQL")
            return anomaly.to_dict()
        except Exception as e:
            logger.error(f"Failed to create anomaly result: {e}")
            raise
    
    async def get_by_id(self, anomaly_id: str) -> Optional[Dict[str, Any]]:
        """Get anomaly result by ID."""
        try:
            stmt = select(AnomalyResult).where(AnomalyResult.anomaly_id == anomaly_id)
            result = await self.session.execute(stmt)
            anomaly = result.scalar_one_or_none()
            
            return anomaly.to_dict() if anomaly else None
        except Exception as e:
            logger.error(f"Failed to get anomaly result by ID: {e}")
            raise
    
    async def get_by_transaction_id(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get anomaly result by transaction ID or transaction hash (tries hash first)."""
        try:
            # The caller may pass either a transaction_hash or a transaction_id.
            # Try transaction_hash first (frontend passes the hash from the URL).
            stmt = select(AnomalyResult).where(
                AnomalyResult.transaction_hash == transaction_id
            ).order_by(AnomalyResult.detected_at.desc())
            result = await self.session.execute(stmt)
            anomaly = result.scalars().first()

            if anomaly is None:
                # Fall back to querying by internal transaction_id
                stmt = select(AnomalyResult).where(
                    AnomalyResult.transaction_id == transaction_id
                ).order_by(AnomalyResult.detected_at.desc())
                result = await self.session.execute(stmt)
                anomaly = result.scalars().first()

            return anomaly.to_dict() if anomaly else None
        except Exception as e:
            logger.error(f"Failed to get anomaly result by transaction ID/hash: {e}")
            raise

    async def get_by_transaction_hash(self, transaction_hash: str) -> Optional[Dict[str, Any]]:
        """Get anomaly result by transaction hash."""
        try:
            stmt = select(AnomalyResult).where(
                AnomalyResult.transaction_hash == transaction_hash
            ).order_by(AnomalyResult.detected_at.desc())
            result = await self.session.execute(stmt)
            anomaly = result.scalars().first()

            return anomaly.to_dict() if anomaly else None
        except Exception as e:
            logger.error(f"Failed to get anomaly result by transaction hash: {e}")
            raise
    
    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        severity: Optional[str] = None,
        review_status: Optional[str] = None,
        anomaly_category: Optional[str] = None,
        client_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """List anomaly results with filters and pagination."""
        try:
            # Build filters
            filters = []
            if severity:
                filters.append(AnomalyResult.severity == severity)
            if review_status:
                filters.append(AnomalyResult.review_status == review_status)
            if anomaly_category:
                filters.append(AnomalyResult.anomaly_category == anomaly_category)
            if client_id:
                filters.append(AnomalyResult.client_id == client_id)
            if start_date:
                filters.append(AnomalyResult.created_at >= start_date)
            if end_date:
                filters.append(AnomalyResult.created_at <= end_date)
            
            # Count total
            count_stmt = select(func.count(AnomalyResult.anomaly_id))
            if filters:
                count_stmt = count_stmt.where(and_(*filters))
            total_result = await self.session.execute(count_stmt)
            total = total_result.scalar()
            
            # Get paginated results
            stmt = select(AnomalyResult).order_by(AnomalyResult.detected_at.desc())
            if filters:
                stmt = stmt.where(and_(*filters))
            
            stmt = stmt.offset((page - 1) * page_size).limit(page_size)
            result = await self.session.execute(stmt)
            anomalies = result.scalars().all()
            
            return {
                "items": [anomaly.to_dict() for anomaly in anomalies],
                "total": total,
                "page": page,
                "page_size": page_size,
            }
        except Exception as e:
            logger.error(f"Failed to list anomaly results: {e}")
            raise
    
    async def update(self, anomaly_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update anomaly result record."""
        try:
            stmt = select(AnomalyResult).where(AnomalyResult.anomaly_id == anomaly_id)
            result = await self.session.execute(stmt)
            anomaly = result.scalar_one_or_none()
            
            if not anomaly:
                return None
            
            # Update fields
            for key, value in update_data.items():
                if value is not None and hasattr(anomaly, key):
                    setattr(anomaly, key, value)
            
            anomaly.updated_at = datetime.utcnow()
            await self.session.flush()
            await self.session.refresh(anomaly)
            
            logger.info(f"Updated anomaly result {anomaly.anomaly_id}")
            return anomaly.to_dict()
        except Exception as e:
            logger.error(f"Failed to update anomaly result: {e}")
            raise
    
    async def delete(self, anomaly_id: str) -> bool:
        """Delete anomaly result record."""
        try:
            stmt = select(AnomalyResult).where(AnomalyResult.anomaly_id == anomaly_id)
            result = await self.session.execute(stmt)
            anomaly = result.scalar_one_or_none()
            
            if not anomaly:
                return False
            
            await self.session.delete(anomaly)
            await self.session.flush()
            
            logger.info(f"Deleted anomaly result {anomaly_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete anomaly result: {e}")
            raise
    
    async def count_by_severity(self) -> Dict[str, int]:
        """Get count of anomalies by severity."""
        try:
            stmt = select(
                AnomalyResult.severity,
                func.count(AnomalyResult.anomaly_id).label('count')
            ).group_by(AnomalyResult.severity)
            
            result = await self.session.execute(stmt)
            rows = result.all()
            
            return {row.severity: row.count for row in rows}
        except Exception as e:
            logger.error(f"Failed to count by severity: {e}")
            raise
    
    async def count_by_review_status(self) -> Dict[str, int]:
        """Get count of anomalies by review status."""
        try:
            stmt = select(
                AnomalyResult.review_status,
                func.count(AnomalyResult.anomaly_id).label('count')
            ).group_by(AnomalyResult.review_status)
            
            result = await self.session.execute(stmt)
            rows = result.all()
            
            return {row.review_status: row.count for row in rows}
        except Exception as e:
            logger.error(f"Failed to count by review status: {e}")
            raise
    
    async def get_total_count(self) -> int:
        """Get total count of anomalies."""
        try:
            stmt = select(func.count(AnomalyResult.anomaly_id))
            result = await self.session.execute(stmt)
            count = result.scalar()
            return count or 0
        except Exception as e:
            logger.error(f"Failed to get total count: {e}")
            raise
    
    async def get_avg_anomaly_score(self) -> float:
        """Get average anomaly score."""
        try:
            stmt = select(func.avg(AnomalyResult.anomaly_score))
            result = await self.session.execute(stmt)
            avg_score = result.scalar()
            return float(avg_score) if avg_score else 0.0
        except Exception as e:
            logger.error(f"Failed to get average anomaly score: {e}")
            raise
