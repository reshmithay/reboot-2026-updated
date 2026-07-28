-- PostgreSQL Schema for Blockchain Anomaly Detection System
-- Run this to create all tables in PostgreSQL

-- ============================================
-- Transactions Table
-- ============================================
CREATE TABLE IF NOT EXISTS transactions (
    -- Primary identifiers
    id VARCHAR(255) PRIMARY KEY,
    transaction_id VARCHAR(255) NOT NULL UNIQUE,
    transaction_hash VARCHAR(255) NOT NULL UNIQUE,
    
    -- Transaction details
    transaction_type VARCHAR(50) NOT NULL,
    amount NUMERIC(10, 4) NOT NULL,
    currency VARCHAR(10) NOT NULL DEFAULT 'INR',
    transaction_timestamp TIMESTAMP NOT NULL,
    transaction_status VARCHAR(50) NOT NULL,
    on_chain_status VARCHAR(50),
    
    -- Account information
    from_account VARCHAR(255),
    to_account VARCHAR(255),
    from_wallet_address VARCHAR(255),
    to_wallet_address VARCHAR(255),
    wallet_address VARCHAR(255),
    
    -- Client information
    client_id VARCHAR(255),
    client_name VARCHAR(255),
    
    -- Blockchain details
    blockchain_network VARCHAR(100) DEFAULT 'Hyperledger Fabric',
    ledger_type VARCHAR(50) DEFAULT 'Permissioned',
    chain_id INTEGER,
    block_number BIGINT,
    block_hash VARCHAR(255),
    token_symbol VARCHAR(20),
    
    -- Gas and fees
    gas_fee DECIMAL(20, 8),
    gas_price DECIMAL(20, 2),
    
    -- Metadata
    correlation_id VARCHAR(255),
    metadata JSONB,
    
    -- Anomaly detection
    anomaly_score DECIMAL(5, 4),
    is_anomaly BOOLEAN NOT NULL DEFAULT FALSE,
    anomaly_codes TEXT[],  -- Array of anomaly codes
    risk_score INTEGER,
    
    -- Audit timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    CONSTRAINT chk_amount_positive CHECK (amount >= 0),
    CONSTRAINT chk_anomaly_score_range CHECK (anomaly_score >= 0 AND anomaly_score <= 1)
);

-- Create indexes for transactions
CREATE INDEX idx_transactions_transaction_id ON transactions(transaction_id);
CREATE INDEX idx_transactions_transaction_hash ON transactions(transaction_hash);
CREATE INDEX idx_transactions_transaction_type ON transactions(transaction_type);
CREATE INDEX idx_transactions_timestamp ON transactions(transaction_timestamp);
CREATE INDEX idx_transactions_client_id ON transactions(client_id);
CREATE INDEX idx_transactions_from_wallet ON transactions(from_wallet_address);
CREATE INDEX idx_transactions_to_wallet ON transactions(to_wallet_address);
CREATE INDEX idx_transactions_is_anomaly ON transactions(is_anomaly);
CREATE INDEX idx_transactions_transaction_status ON transactions(transaction_status);
CREATE INDEX idx_transactions_block_number ON transactions(block_number);
CREATE INDEX idx_transactions_correlation_id ON transactions(correlation_id);

-- Create GIN index for JSONB metadata
CREATE INDEX idx_transactions_metadata_gin ON transactions USING GIN (metadata);

-- Create composite indexes for common queries
CREATE INDEX idx_transactions_client_timestamp ON transactions(client_id, transaction_timestamp DESC);
CREATE INDEX idx_transactions_anomaly_timestamp ON transactions(is_anomaly, transaction_timestamp DESC);


-- ============================================
-- Client Registry Table
-- ============================================
CREATE TABLE IF NOT EXISTS client_registry (
    -- Primary identifier
    client_id VARCHAR(255) PRIMARY KEY,
    
    -- Basic information
    client_name VARCHAR(255) NOT NULL,
    client_type VARCHAR(100),
    lei VARCHAR(20),  -- Legal Entity Identifier
    industry_sector VARCHAR(100),
    country_of_incorporation VARCHAR(100),
    
    -- Risk and relationship
    risk_tier VARCHAR(50),
    relationship_manager VARCHAR(255),
    
    -- Wallet information
    wallet_address VARCHAR(255),
    wallet_type VARCHAR(50),
    
    -- Facility details
    facility_type VARCHAR(100),
    credit_limit DECIMAL(20, 2) DEFAULT 0,
    daily_deposit_limit DECIMAL(20, 2) DEFAULT 0,
    daily_withdrawal_limit DECIMAL(20, 2) DEFAULT 0,
    
    -- Operating parameters
    expected_activity_window VARCHAR(255),  -- e.g., "09:00-17:00 UTC"
    authorized_signatories JSONB,  -- Array of authorized persons
    
    -- Compliance status
    kyc_status VARCHAR(50),
    aml_status VARCHAR(50),
    
    -- Audit timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_credit_limit_positive CHECK (credit_limit >= 0),
    CONSTRAINT chk_daily_deposit_positive CHECK (daily_deposit_limit >= 0),
    CONSTRAINT chk_daily_withdrawal_positive CHECK (daily_withdrawal_limit >= 0)
);

-- Create indexes for client registry
CREATE INDEX idx_client_registry_client_name ON client_registry(client_name);
CREATE INDEX idx_client_registry_wallet_address ON client_registry(wallet_address);
CREATE INDEX idx_client_registry_risk_tier ON client_registry(risk_tier);
CREATE INDEX idx_client_registry_kyc_status ON client_registry(kyc_status);
CREATE INDEX idx_client_registry_aml_status ON client_registry(aml_status);
CREATE INDEX idx_client_registry_client_type ON client_registry(client_type);

-- Create GIN index for authorized signatories
CREATE INDEX idx_client_registry_signatories_gin ON client_registry USING GIN (authorized_signatories);


-- ============================================
-- Anomaly Master Table
-- ============================================
CREATE TABLE IF NOT EXISTS anomaly_master (
    -- Primary identifier
    anomaly_code VARCHAR(50) PRIMARY KEY,
    
    -- Classification
    category VARCHAR(100) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    risk_score INTEGER NOT NULL,
    
    -- Description
    description TEXT,
    
    -- Status
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    
    -- Audit timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_risk_score_range CHECK (risk_score >= 0 AND risk_score <= 100)
);

-- Create indexes for anomaly master
CREATE INDEX idx_anomaly_master_category ON anomaly_master(category);
CREATE INDEX idx_anomaly_master_severity ON anomaly_master(severity);
CREATE INDEX idx_anomaly_master_is_active ON anomaly_master(is_active);
CREATE INDEX idx_anomaly_master_risk_score ON anomaly_master(risk_score);


-- ============================================
-- Create updated_at trigger function
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables
CREATE TRIGGER update_transactions_updated_at
    BEFORE UPDATE ON transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_client_registry_updated_at
    BEFORE UPDATE ON client_registry
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_anomaly_master_updated_at
    BEFORE UPDATE ON anomaly_master
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- ============================================
-- Sample Data for Anomaly Master
-- ============================================
INSERT INTO anomaly_master (anomaly_code, category, severity, risk_score, description, is_active) VALUES
    ('AN001', 'Off-Hours Transaction', 'MEDIUM', 60, 'Transaction occurred outside expected business hours', true),
    ('AN002', 'Threshold Deposit', 'HIGH', 85, 'Deposit amount exceeds configured threshold', true),
    ('AN003', 'Duplicate Escrow', 'CRITICAL', 95, 'Duplicate escrow payment detected', true),
    ('AN004', 'Oracle Manipulation', 'CRITICAL', 98, 'Potential oracle price manipulation detected', true),
    ('AN005', 'Daily Limit Breach', 'HIGH', 80, 'Daily transaction limit exceeded', true),
    ('AN006', 'Reconciliation Mismatch', 'MEDIUM', 70, 'Reconciliation discrepancy detected', true),
    ('AN007', 'Full Withdrawal', 'HIGH', 85, 'Full account withdrawal detected', true),
    ('AN008', 'Time Window Violation', 'MEDIUM', 65, 'Transaction outside allowed time window', true),
    ('AN009', 'Rapid Transaction', 'MEDIUM', 70, 'Multiple transactions in short time period', true),
    ('AN010', 'Unusual Amount', 'MEDIUM', 65, 'Transaction amount deviates from normal pattern', true)
ON CONFLICT (anomaly_code) DO NOTHING;


-- ============================================
-- Views for common queries
-- ============================================

-- View: Recent anomalies with client details
CREATE OR REPLACE VIEW v_recent_anomalies AS
SELECT 
    t.transaction_id,
    t.transaction_hash,
    t.transaction_type,
    t.amount,
    t.currency,
    t.transaction_timestamp,
    t.anomaly_score,
    t.anomaly_codes,
    c.client_name,
    c.risk_tier,
    c.wallet_address
FROM transactions t
LEFT JOIN client_registry c ON t.client_id = c.client_id
WHERE t.is_anomaly = TRUE
ORDER BY t.transaction_timestamp DESC;

-- View: Client transaction summary
CREATE OR REPLACE VIEW v_client_transaction_summary AS
SELECT 
    c.client_id,
    c.client_name,
    c.risk_tier,
    COUNT(t.id) as total_transactions,
    SUM(CASE WHEN t.is_anomaly THEN 1 ELSE 0 END) as anomaly_count,
    SUM(t.amount) as total_amount,
    MAX(t.transaction_timestamp) as last_transaction_date
FROM client_registry c
LEFT JOIN transactions t ON c.client_id = t.client_id
GROUP BY c.client_id, c.client_name, c.risk_tier;

-- View: Daily anomaly statistics
CREATE OR REPLACE VIEW v_daily_anomaly_stats AS
SELECT 
    DATE(transaction_timestamp) as transaction_date,
    COUNT(*) as total_transactions,
    SUM(CASE WHEN is_anomaly THEN 1 ELSE 0 END) as anomaly_count,
    ROUND(AVG(CASE WHEN is_anomaly THEN 1.0 ELSE 0.0 END) * 100, 2) as anomaly_percentage,
    SUM(amount) as total_amount,
    SUM(CASE WHEN is_anomaly THEN amount ELSE 0 END) as anomaly_amount
FROM transactions
GROUP BY DATE(transaction_timestamp)
ORDER BY transaction_date DESC;


-- ============================================
-- Grant permissions (adjust as needed)
-- ============================================
-- GRANT SELECT, INSERT, UPDATE, DELETE ON transactions TO app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON client_registry TO app_user;
-- GRANT SELECT ON anomaly_master TO app_user;
