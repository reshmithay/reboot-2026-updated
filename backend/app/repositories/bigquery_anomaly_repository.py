"""
BigQuery repository implementation for anomaly results.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from google.cloud import bigquery

from app.config.settings import Settings
from app.utilities.logger.logger import get_logger

logger = get_logger(__name__)
settings = Settings()


class BigQueryAnomalyRepository:
    """BigQuery implementation of anomaly results repository."""
    
    def __init__(self):
        try:
            self.client = bigquery.Client(project=settings.BIGQUERY_PROJECT_ID)
            self.table_id = f"{settings.BIGQUERY_PROJECT_ID}.{settings.BIGQUERY_DATASET}.{settings.BIGQUERY_ANOMALY_TABLE}"
            logger.info(f"BigQuery client initialized for table {self.table_id}")
        except Exception as e:
            logger.warning(f"BigQuery client initialization failed: {e}")
            self.client = None
    
    async def create(self, anomaly_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new anomaly result record in BigQuery."""
        if not self.client:
            raise RuntimeError("BigQuery client not initialized")
        
        try:
            # Convert datetime objects to strings
            row_data = anomaly_data.copy()
            for key in ["detected_at", "reviewed_at", "created_at"]:
                if key in row_data and isinstance(row_data[key], datetime):
                    row_data[key] = row_data[key].isoformat()
            
            rows_to_insert = [row_data]
            errors = self.client.insert_rows_json(self.table_id, rows_to_insert)
            
            if errors:
                logger.error(f"BigQuery insert errors: {errors}")
                raise RuntimeError(f"Failed to insert into BigQuery: {errors}")
            
            logger.info(f"Created anomaly result {anomaly_data.get('anomaly_id')} in BigQuery")
            return anomaly_data
        except Exception as e:
            logger.error(f"Failed to create anomaly result in BigQuery: {e}")
            raise
    
    async def get_by_id(self, anomaly_id: str) -> Optional[Dict[str, Any]]:
        """Get anomaly result by ID from BigQuery."""
        if not self.client:
            raise RuntimeError("BigQuery client not initialized")
        
        try:
            query = f"""
                SELECT *
                FROM `{self.table_id}`
                WHERE anomaly_id = @anomaly_id
                LIMIT 1
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("anomaly_id", "STRING", anomaly_id)
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = list(query_job.result())
            
            if not results:
                return None
            
            return dict(results[0])
        except Exception as e:
            logger.error(f"Failed to get anomaly result from BigQuery: {e}")
            raise
    
    async def get_by_transaction_id(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get anomaly result by transaction ID or transaction hash (tries hash first)."""
        if not self.client:
            raise RuntimeError("BigQuery client not initialized")

        try:
            # Try transaction_hash first (frontend passes the hash from the URL)
            query = f"""
                SELECT *
                FROM `{self.table_id}`
                WHERE transaction_hash = @value
                ORDER BY detected_at DESC
                LIMIT 1
            """
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("value", "STRING", transaction_id)
                ]
            )
            query_job = self.client.query(query, job_config=job_config)
            results = list(query_job.result())

            if results:
                return dict(results[0])

            # Fall back to internal transaction_id
            query = f"""
                SELECT *
                FROM `{self.table_id}`
                WHERE transaction_id = @value
                ORDER BY detected_at DESC
                LIMIT 1
            """
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("value", "STRING", transaction_id)
                ]
            )
            query_job = self.client.query(query, job_config=job_config)
            results = list(query_job.result())

            return dict(results[0]) if results else None
        except Exception as e:
            logger.error(f"Failed to get anomaly result by transaction ID/hash: {e}")
            raise
    
    async def get_by_transaction_hash(self, transaction_hash: str) -> Optional[Dict[str, Any]]:
        """Get anomaly result by transaction hash."""
        if not self.client:
            raise RuntimeError("BigQuery client not initialized")
        
        try:
            query = f"""
                SELECT *
                FROM `{self.table_id}`
                WHERE transaction_hash = @transaction_hash
                ORDER BY detected_at DESC
                LIMIT 1
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("transaction_hash", "STRING", transaction_hash)
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = list(query_job.result())
            
            if not results:
                return None
            
            return dict(results[0])
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
        if not self.client:
            raise RuntimeError("BigQuery client not initialized")
        
        try:
            # Build WHERE clause
            where_clauses = []
            query_parameters = []
            
            if severity:
                where_clauses.append("severity = @severity")
                query_parameters.append(bigquery.ScalarQueryParameter("severity", "STRING", severity))
            
            if review_status:
                where_clauses.append("review_status = @review_status")
                query_parameters.append(bigquery.ScalarQueryParameter("review_status", "STRING", review_status))
            
            if anomaly_category:
                where_clauses.append("anomaly_category = @anomaly_category")
                query_parameters.append(bigquery.ScalarQueryParameter("anomaly_category", "STRING", anomaly_category))
            
            if client_id:
                where_clauses.append("client_id = @client_id")
                query_parameters.append(bigquery.ScalarQueryParameter("client_id", "STRING", client_id))
            
            if start_date:
                where_clauses.append("detected_at >= @start_date")
                query_parameters.append(bigquery.ScalarQueryParameter("start_date", "TIMESTAMP", start_date))
            
            if end_date:
                where_clauses.append("detected_at <= @end_date")
                query_parameters.append(bigquery.ScalarQueryParameter("end_date", "TIMESTAMP", end_date))
            
            where_clause = " AND ".join(where_clauses) if where_clauses else "TRUE"
            
            # Count query
            count_query = f"""
                SELECT COUNT(*) as total
                FROM `{self.table_id}`
                WHERE {where_clause}
            """
            
            # Data query
            offset = (page - 1) * page_size
            data_query = f"""
                SELECT *
                FROM `{self.table_id}`
                WHERE {where_clause}
                ORDER BY detected_at DESC
                LIMIT @page_size
                OFFSET @offset
            """
            
            query_parameters.extend([
                bigquery.ScalarQueryParameter("page_size", "INT64", page_size),
                bigquery.ScalarQueryParameter("offset", "INT64", offset)
            ])
            
            # Execute count query
            count_job_config = bigquery.QueryJobConfig(query_parameters=query_parameters[:len(where_clauses)])
            count_job = self.client.query(count_query, job_config=count_job_config)
            count_results = list(count_job.result())
            total = count_results[0]["total"] if count_results else 0
            
            # Execute data query
            data_job_config = bigquery.QueryJobConfig(query_parameters=query_parameters)
            data_job = self.client.query(data_query, job_config=data_job_config)
            items = [dict(row) for row in data_job.result()]
            
            return {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0
            }
        except Exception as e:
            logger.error(f"Failed to list anomaly results from BigQuery: {e}")
            raise
    
    async def update(self, anomaly_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update anomaly result (Note: BigQuery uses DELETE + INSERT for updates)."""
        if not self.client:
            raise RuntimeError("BigQuery client not initialized")
        
        try:
            # Get existing record
            existing = await self.get_by_id(anomaly_id)
            if not existing:
                return None
            
            # Merge update data
            updated_data = {**existing, **update_data}
            
            # Delete old record
            delete_query = f"""
                DELETE FROM `{self.table_id}`
                WHERE anomaly_id = @anomaly_id
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("anomaly_id", "STRING", anomaly_id)
                ]
            )
            
            delete_job = self.client.query(delete_query, job_config=job_config)
            delete_job.result()
            
            # Insert updated record
            await self.create(updated_data)
            
            logger.info(f"Updated anomaly result {anomaly_id} in BigQuery")
            return updated_data
        except Exception as e:
            logger.error(f"Failed to update anomaly result in BigQuery: {e}")
            raise
    
    async def count_by_severity(self) -> Dict[str, int]:
        """Get count of anomalies by severity."""
        if not self.client:
            raise RuntimeError("BigQuery client not initialized")
        
        try:
            query = f"""
                SELECT severity, COUNT(*) as count
                FROM `{self.table_id}`
                GROUP BY severity
            """
            
            query_job = self.client.query(query)
            results = query_job.result()
            
            severity_counts = {}
            for row in results:
                severity_counts[row.severity] = row.count
            
            logger.info(f"Retrieved severity counts from BigQuery")
            return severity_counts
        except Exception as e:
            logger.error(f"Failed to count by severity in BigQuery: {e}")
            raise
    
    async def count_by_review_status(self) -> Dict[str, int]:
        """Get count of anomalies by review status."""
        if not self.client:
            raise RuntimeError("BigQuery client not initialized")
        
        try:
            query = f"""
                SELECT review_status, COUNT(*) as count
                FROM `{self.table_id}`
                GROUP BY review_status
            """
            
            query_job = self.client.query(query)
            results = query_job.result()
            
            status_counts = {}
            for row in results:
                status_counts[row.review_status] = row.count
            
            logger.info(f"Retrieved review status counts from BigQuery")
            return status_counts
        except Exception as e:
            logger.error(f"Failed to count by review status in BigQuery: {e}")
            raise
    
    async def get_total_count(self) -> int:
        """Get total count of anomalies."""
        if not self.client:
            raise RuntimeError("BigQuery client not initialized")
        
        try:
            query = f"""
                SELECT COUNT(*) as total
                FROM `{self.table_id}`
            """
            
            query_job = self.client.query(query)
            results = query_job.result()
            
            for row in results:
                return row.total
            return 0
        except Exception as e:
            logger.error(f"Failed to get total count in BigQuery: {e}")
            raise
    
    async def get_avg_anomaly_score(self) -> float:
        """Get average anomaly score."""
        if not self.client:
            raise RuntimeError("BigQuery client not initialized")
        
        try:
            query = f"""
                SELECT AVG(anomaly_score) as avg_score
                FROM `{self.table_id}`
            """
            
            query_job = self.client.query(query)
            results = query_job.result()
            
            for row in results:
                return float(row.avg_score) if row.avg_score else 0.0
            return 0.0
        except Exception as e:
            logger.error(f"Failed to get average anomaly score in BigQuery: {e}")
            raise
