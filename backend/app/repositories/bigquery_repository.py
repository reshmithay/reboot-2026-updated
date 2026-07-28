"""
BigQuery repository implementation for transactions.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from google.cloud import bigquery

from app.repositories.base_repository import BaseTransactionRepository
from app.config.settings import Settings
from app.utilities.logger.logger import get_logger

logger = get_logger(__name__)
settings = Settings()


class BigQueryTransactionRepository(BaseTransactionRepository):
    """BigQuery implementation of transaction repository."""
    
    def __init__(self):
        try:
            self.client = bigquery.Client(project=settings.BIGQUERY_PROJECT_ID)
            self.table_id = f"{settings.BIGQUERY_PROJECT_ID}.{settings.BIGQUERY_DATASET}.{settings.BIGQUERY_TABLE}"
            logger.info(f"BigQuery client initialized for table {self.table_id}")
        except Exception as e:
            logger.warning(f"BigQuery client initialization failed: {e}")
            self.client = None
    
    async def create(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new transaction record in BigQuery."""
        if not self.client:
            raise RuntimeError("BigQuery client not initialized")
        
        try:
            # Convert datetime objects to strings
            row_data = transaction_data.copy()
            if "transaction_timestamp" in row_data and isinstance(row_data["transaction_timestamp"], datetime):
                row_data["transaction_timestamp"] = row_data["transaction_timestamp"].isoformat()
            
            rows_to_insert = [row_data]
            errors = self.client.insert_rows_json(self.table_id, rows_to_insert)
            
            if errors:
                logger.error(f"BigQuery insert errors: {errors}")
                raise RuntimeError(f"Failed to insert into BigQuery: {errors}")
            
            logger.info(f"Created transaction {transaction_data.get('transaction_hash')} in BigQuery")
            return transaction_data
        except Exception as e:
            logger.error(f"Failed to create transaction in BigQuery: {e}")
            raise
    
    async def get_by_id(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get transaction by ID from BigQuery."""
        if not self.client:
            raise RuntimeError("BigQuery client not initialized")
        
        try:
            query = f"""
                SELECT *
                FROM `{self.table_id}`
                WHERE id = @transaction_id
                LIMIT 1
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("transaction_id", "STRING", transaction_id)
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = list(query_job.result())
            
            if not results:
                return None
            
            return dict(results[0])
        except Exception as e:
            logger.error(f"Failed to get transaction from BigQuery: {e}")
            raise
    
    async def get_by_hash(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """Get transaction by hash from BigQuery."""
        if not self.client:
            raise RuntimeError("BigQuery client not initialized")
        
        try:
            query = f"""
                SELECT *
                FROM `{self.table_id}`
                WHERE transaction_hash = @transaction_hash
                LIMIT 1
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("transaction_hash", "STRING", tx_hash)
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = list(query_job.result())
            
            if not results:
                return None
            
            return dict(results[0])
        except Exception as e:
            logger.error(f"Failed to get transaction from BigQuery: {e}")
            raise
    
    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        is_anomaly: Optional[bool] = None,
        chain_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """List transactions from BigQuery with filters and pagination."""
        if not self.client:
            raise RuntimeError("BigQuery client not initialized")
        
        try:
            # Build WHERE clauses
            where_clauses = []
            query_params = []
            
            # Note: is_anomaly field not in current schema
            
            if chain_id is not None:
                where_clauses.append("chain_id = @chain_id")
                query_params.append(bigquery.ScalarQueryParameter("chain_id", "INT64", chain_id))
            
            if start_date:
                where_clauses.append("transaction_timestamp >= @start_date")
                query_params.append(bigquery.ScalarQueryParameter("start_date", "TIMESTAMP", start_date))
            
            if end_date:
                where_clauses.append("transaction_timestamp <= @end_date")
                query_params.append(bigquery.ScalarQueryParameter("end_date", "TIMESTAMP", end_date))
            
            where_clause = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
            
            # Count query
            count_query = f"""
                SELECT COUNT(*) as total
                FROM `{self.table_id}`
                {where_clause}
            """
            
            job_config = bigquery.QueryJobConfig(query_parameters=query_params)
            count_job = self.client.query(count_query, job_config=job_config)
            total = list(count_job.result())[0]["total"]
            
            # Data query with pagination
            offset = (page - 1) * page_size
            query = f"""
                SELECT *
                FROM `{self.table_id}`
                {where_clause}
                ORDER BY transaction_timestamp DESC
                LIMIT @page_size
                OFFSET @offset
            """
            
            query_params.extend([
                bigquery.ScalarQueryParameter("page_size", "INT64", page_size),
                bigquery.ScalarQueryParameter("offset", "INT64", offset),
            ])
            
            job_config = bigquery.QueryJobConfig(query_parameters=query_params)
            query_job = self.client.query(query, job_config=job_config)
            results = [dict(row) for row in query_job.result()]
            
            return {
                "items": results,
                "total": total,
                "page": page,
                "page_size": page_size,
            }
        except Exception as e:
            logger.error(f"Failed to list transactions from BigQuery: {e}")
            raise
    
    async def update(self, transaction_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update transaction in BigQuery (using MERGE statement)."""
        if not self.client:
            raise RuntimeError("BigQuery client not initialized")
        
        # BigQuery doesn't support direct updates easily, would need MERGE statement
        # For now, log a warning
        logger.warning("BigQuery updates not fully implemented, returning None")
        return None
    
    async def delete(self, transaction_id: str) -> bool:
        """Delete transaction from BigQuery."""
        if not self.client:
            raise RuntimeError("BigQuery client not initialized")
        
        try:
            query = f"""
                DELETE FROM `{self.table_id}`
                WHERE id = @transaction_id
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("transaction_id", "STRING", transaction_id)
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            query_job.result()  # Wait for completion
            
            logger.info(f"Deleted transaction {transaction_id} from BigQuery")
            return True
        except Exception as e:
            logger.error(f"Failed to delete transaction from BigQuery: {e}")
            return False
    
    async def count(self, is_anomaly: Optional[bool] = None, chain_id: Optional[int] = None) -> int:
        """Count transactions in BigQuery with optional filters."""
        if not self.client:
            raise RuntimeError("BigQuery client not initialized")
        
        try:
            where_clauses = []
            query_params = []
            
            # Note: is_anomaly field not in current schema
            
            if chain_id is not None:
                where_clauses.append("chain_id = @chain_id")
                query_params.append(bigquery.ScalarQueryParameter("chain_id", "INT64", chain_id))
            
            where_clause = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
            
            query = f"""
                SELECT COUNT(*) as count
                FROM `{self.table_id}`
                {where_clause}
            """
            
            job_config = bigquery.QueryJobConfig(query_parameters=query_params)
            query_job = self.client.query(query, job_config=job_config)
            result = list(query_job.result())[0]
            
            return result["count"]
        except Exception as e:
            logger.error(f"Failed to count transactions in BigQuery: {e}")
            raise
