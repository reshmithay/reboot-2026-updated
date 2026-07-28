import pandas as pd
import uuid
from datetime import datetime, timezone
from sqlalchemy import create_engine, inspect

# 1. Read your dataset
df = pd.read_csv("ml-engine/datasets/transactions.csv") 

# 2. Map ML columns to the exact SQLAlchemy model columns
column_mapping = {
    "tx_hash": "transaction_hash",
    "from_address": "from_wallet_address",
    "to_address": "to_wallet_address",
    "value": "amount",
    "timestamp": "transaction_timestamp",
}
df = df.rename(columns=column_mapping)

# --- NEW FIX: Prevent Numeric Overflow ---
# Cap the maximum amount to 999,999.99 so it fits inside DECIMAL(10,4)
if 'amount' in df.columns:
    df['amount'] = df['amount'].clip(upper=999999.99)
# -----------------------------------------

# 3. Fulfill all 'nullable=False' requirements from your model
if 'id' in df.columns:
    df['transaction_id'] = df['id']
else:
    df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]
    df['transaction_id'] = df['id']

df['transaction_type'] = 'TRANSFER'      
df['transaction_status'] = 'COMPLETED'   
df['currency'] = 'USD'                   
df['blockchain_network'] = 'Polygon'     

# Fix timezone warning using timezone-aware UTC
current_time = datetime.now(timezone.utc)
df['transaction_timestamp'] = pd.to_datetime(df['transaction_timestamp'])
df['created_at'] = current_time
df['updated_at'] = current_time

# 4. Connect to Neon
DATABASE_URL = "postgresql://neondb_owner:npg_VdRFLQW7qJ1U@ep-soft-field-ax5p830f.c-4.us-east-2.aws.neon.tech/neondb"
engine = create_engine(DATABASE_URL)

# 5. Filter out ML-specific columns that don't belong in the DB
inspector = inspect(engine)
db_columns = [col['name'] for col in inspector.get_columns('transactions')]

valid_cols = [col for col in df.columns if col in db_columns]
df_filtered = df[valid_cols]

print(f"Uploading mapped columns: {valid_cols}")

# 6. Upload directly to transactions table!
df_filtered.to_sql("transactions", con=engine, if_exists="append", index=False)
print(f"Successfully uploaded {len(df_filtered)} transactions to Neon database!")