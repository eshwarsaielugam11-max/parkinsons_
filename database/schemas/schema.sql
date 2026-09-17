BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 81e642445c47

CREATE TABLE patients (
    id VARCHAR NOT NULL, 
    age_bucket VARCHAR, 
    sex VARCHAR, 
    PRIMARY KEY (id)
);

CREATE TABLE sessions (
    id VARCHAR NOT NULL, 
    patient_id VARCHAR NOT NULL, 
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL, 
    task_type VARCHAR NOT NULL, 
    mode VARCHAR NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(patient_id) REFERENCES patients (id) ON DELETE CASCADE
);

CREATE TABLE recordings (
    id VARCHAR NOT NULL, 
    session_id VARCHAR NOT NULL, 
    storage_ref VARCHAR NOT NULL, 
    audio_quality_score FLOAT, 
    retention_expires_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(session_id) REFERENCES sessions (id) ON DELETE CASCADE
);

CREATE TABLE reports (
    id VARCHAR NOT NULL, 
    session_id VARCHAR NOT NULL, 
    prediction JSON, 
    structured_evidence JSON, 
    generated_report_text VARCHAR, 
    model_version VARCHAR NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(session_id) REFERENCES sessions (id) ON DELETE CASCADE, 
    UNIQUE (session_id)
);

INSERT INTO alembic_version (version_num) VALUES ('81e642445c47') RETURNING alembic_version.version_num;

COMMIT;

