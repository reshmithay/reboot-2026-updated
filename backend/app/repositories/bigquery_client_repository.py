"""
BigQuery repository implementation for client registry.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from google.cloud import bigquery

from app.config.settings import Settings
from app.utilities.logger.logger import get_logger

logger = get_logger(__name__)
settings = Settings()


class BigQueryClientRepository:
    """BigQuery implementation of client registry repository."""
    
    def __init__(self):
        try:
            self.client = bigquery.Client(project=settings.BIGQUERY_PROJECT_ID)
            self.table_id = f"{settings.BIGQUERY_PROJECT_ID}.{settings.BIGQUERY_DATASET}.{settings.BIGQUERY_CLIENT_TABLE}"
            logger.info(f"BigQuery client initialized for table {self.table_id}")
        except Exception as e:
            logger.warning(f"BigQuery client initialization failed: {e}")
            self.client = None
    
    async def create(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new client record in BigQuery."""
        if not self.client:
            raise RuntimeError("BigQuery client not initialized")
        
        try:
            # Convert datetime objects to strings
            row_data = client_data.copy()
            for key in ["onboarding_date", "last_review_date", "created_at", "updated_at"]:
                if key in row_data and isinstance(row_data[key], datetime):
                    row_data[key] = row_data[key].isoformat()
            
            rows_to_insert = [row_data]
            errors = self.client.insert_rows_json(self.table_id, rows_to_insert)
            
            if errors:
                logger.error(f"BigQuery insert errors: {errors}")
                raise RuntimeError(f"Failed to insert into BigQuery: {errors}")
            
            logger.info(f"Created client {client_data.get('client_id')} in BigQuery")
            return client_data
        except Exception as e:
            logger.error(f"Failed to create client in BigQuery: {e}")
            raise
    
    async def get_by_id(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get client by ID from BigQuery."""
        if not self.client:
            raise RuntimeError("BigQuery client not initialized")
        
        try:
            query = f"""
                SELECT *
                FROM `{self.table_id}`
                WHERE client_id = @client_id
                LIMIT 1
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("client_id", "STRING", client_id)
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = list(query_job.result())
            
            if not results:
                return None
            
            return dict(results[0])
        except Exception as e:
            logger.error(f"Failed to get client from BigQuery: {e}")
            raise
    
    async def get_by_wallet(self, wallet_address: str) -> Optional[Dict[str, Any]]:
        """Get client by wallet address from BigQuery."""
        if not self.client:
            raise RuntimeError("BigQuery client not initialized")
        
        try:
            query = f"""
                SELECT *
                FROM `{self.table_id}`
                WHERE wallet_address = @wallet_address
                LIMIT 1
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("wallet_address", "STRING", wallet_address)
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = list(query_job.result())
            
            if not results:
                return None
            
            return dict(results[0])
        except Exception as e:
            logger.error(f"Failed to get client by wallet from BigQuery: {e}")
            raise
    
    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        risk_tier: Optional[str] = None,
        kyc_status: Optional[str] = None,
        aml_status: Optional[str] = None,
        client_type: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List clients with filters and pagination."""
        if not self.client:
            raise RuntimeError("BigQuery client not initialized")
        
        try:
            # Build WHERE clause
            where_clauses = []
            query_parameters = []
            
            if risk_tier:
                where_clauses.append("risk_tier = @risk_tier")
                query_parameters.append(bigquery.ScalarQueryParameter("risk_tier", "STRING", risk_tier))
            
            if kyc_status:
                where_clauses.append("kyc_status = @kyc_status")
                query_parameters.append(bigquery.ScalarQueryParameter("kyc_status", "STRING", kyc_status))
            
            if aml_status:
                where_clauses.append("aml_status = @aml_status")
                query_parameters.append(bigquery.ScalarQueryParameter("aml_status", "STRING", aml_status))
            
            if client_type:
                where_clauses.append("client_type = @client_type")
                query_parameters.append(bigquery.ScalarQueryParameter("client_type", "STRING", client_type))
            
            if search:
                where_clauses.append(
                    "(LOWER(client_name) LIKE @search OR "
                    "LOWER(client_id) LIKE @search OR "
                    "LOWER(wallet_address) LIKE @search)"
                )
                query_parameters.append(bigquery.ScalarQueryParameter("search", "STRING", f"%{search.lower()}%"))
            
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
                ORDER BY client_name
                LIMIT @page_size
                OFFSET @offset
            """
            
            query_parameters.extend([
                bigquery.ScalarQueryParameter("page_size", "INT64", page_size),
                bigquery.ScalarQueryParameter("offset", "INT64", offset)
            ])
            
            # Execute count query (without pagination params)
            count_job_config = bigquery.QueryJobConfig(
                query_parameters=[p for p in query_parameters if p.name not in ["page_size", "offset"]]
            )
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
            logger.error(f"Failed to list clients from BigQuery: {e}")
            raise
    
    async def update(self, client_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update client record (Note: BigQuery uses DELETE + INSERT for updates)."""
        if not self.client:
            raise RuntimeError("BigQuery client not initialized")
        
        try:
            # Get existing record
            existing = await self.get_by_id(client_id)
            if not existing:
                return None
            
            # Merge update data
            updated_data = {**existing, **update_data}
            updated_data["updated_at"] = datetime.utcnow().isoformat()
            
            # Delete old record
            delete_query = f"""
                DELETE FROM `{self.table_id}`
                WHERE client_id = @client_id
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("client_id", "STRING", client_id)
                ]
            )
            
            delete_job = self.client.query(delete_query, job_config=job_config)
            delete_job.result()
            
            # Insert updated record
            await self.create(updated_data)
            
            logger.info(f"Updated client {client_id} in BigQuery")
            return updated_data
        except Exception as e:
            logger.error(f"Failed to update client in BigQuery: {e}")
            raise
    
    async def update_risk_score(self, client_id: str, risk_score: float, risk_tier: str) -> Optional[Dict[str, Any]]:
        """Update client risk score and tier."""
        return await self.update(client_id, {
            "risk_score": risk_score,
            "risk_tier": risk_tier,
            "last_review_date": datetime.utcnow().isoformat()
        })
