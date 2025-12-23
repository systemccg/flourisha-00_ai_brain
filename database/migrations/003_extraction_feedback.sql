-- ============================================================================
-- Extraction Feedback System
-- Enables continuous improvement through human review and automated validation
-- ============================================================================

-- 1. Extraction Feedback Table
-- Stores corrections from human review
CREATE TABLE IF NOT EXISTS mrl_extraction_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES mrl_documents(id),

    -- What was extracted
    field_name TEXT NOT NULL,  -- e.g., 'companies', 'contacts', 'properties'
    extracted_value JSONB,     -- What Claude extracted

    -- What it should have been
    corrected_value JSONB,     -- Human correction
    correction_type TEXT NOT NULL,  -- 'missing', 'incorrect', 'extra', 'wrong_field'

    -- Context for learning
    correction_notes TEXT,     -- Why this was wrong
    document_context TEXT,     -- Relevant text from document

    -- Metadata
    reviewed_by TEXT,
    reviewed_at TIMESTAMPTZ DEFAULT NOW(),
    used_for_training BOOLEAN DEFAULT FALSE,

    tenant_id TEXT DEFAULT 'default',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_extraction_feedback_field ON mrl_extraction_feedback(field_name);
CREATE INDEX idx_extraction_feedback_type ON mrl_extraction_feedback(correction_type);
CREATE INDEX idx_extraction_feedback_training ON mrl_extraction_feedback(used_for_training);

-- 2. Few-Shot Examples Table
-- Curated examples for prompt injection
CREATE TABLE IF NOT EXISTS mrl_extraction_examples (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Example metadata
    example_name TEXT NOT NULL,
    document_category TEXT NOT NULL,  -- 'insurance', 'financial', 'legal', etc.
    difficulty TEXT DEFAULT 'standard',  -- 'simple', 'standard', 'complex'

    -- The example content
    document_description TEXT NOT NULL,  -- Brief description of document
    document_snippet TEXT,               -- Key text from document (anonymized)

    -- Expected extraction (gold standard)
    expected_extraction JSONB NOT NULL,  -- Full DocumentExtraction as JSON

    -- Usage tracking
    times_used INTEGER DEFAULT 0,
    success_rate FLOAT,  -- How often using this example improves accuracy

    -- Control
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 50,  -- Higher = more likely to be included

    tenant_id TEXT DEFAULT 'default',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_extraction_examples_category ON mrl_extraction_examples(document_category);
CREATE INDEX idx_extraction_examples_active ON mrl_extraction_examples(is_active, priority DESC);

-- 3. Validation Rules Table
-- Rules for automated validation against known entities
CREATE TABLE IF NOT EXISTS mrl_validation_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    rule_name TEXT NOT NULL,
    rule_type TEXT NOT NULL,  -- 'entity_exists', 'field_format', 'cross_reference'

    -- Rule definition
    entity_type TEXT,         -- 'company', 'contact', 'property'
    field_to_check TEXT,      -- Which extracted field to validate
    validation_query TEXT,    -- SQL or logic to check

    -- What to do when validation fails
    on_failure TEXT DEFAULT 'flag_review',  -- 'flag_review', 'auto_correct', 'warn'
    severity TEXT DEFAULT 'medium',         -- 'low', 'medium', 'high'

    is_active BOOLEAN DEFAULT TRUE,

    tenant_id TEXT DEFAULT 'default',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Validation Results Table
-- Track validation outcomes for each extraction
CREATE TABLE IF NOT EXISTS mrl_validation_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES mrl_documents(id),
    rule_id UUID REFERENCES mrl_validation_rules(id),

    passed BOOLEAN NOT NULL,
    details JSONB,  -- What was checked and result

    -- If auto-corrected
    auto_corrected BOOLEAN DEFAULT FALSE,
    original_value JSONB,
    corrected_value JSONB,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_validation_results_doc ON mrl_validation_results(document_id);
CREATE INDEX idx_validation_results_passed ON mrl_validation_results(passed);

-- 5. Insert default validation rules
INSERT INTO mrl_validation_rules (rule_name, rule_type, entity_type, field_to_check, validation_query, on_failure, severity) VALUES
-- Check if extracted property exists in known properties
('known_property_check', 'entity_exists', 'property', 'properties',
 'SELECT id FROM mrl_properties WHERE full_address ILIKE $1 OR $1 = ANY(aliases)',
 'flag_review', 'medium'),

-- Check if company name matches known companies
('known_company_check', 'entity_exists', 'company', 'companies',
 'SELECT id FROM mrl_companies WHERE compname ILIKE $1',
 'flag_review', 'low'),

-- Validate property addresses from filename match extraction
('filename_property_match', 'cross_reference', 'property', 'resolved_property',
 'Check if resolved property from filename matches extracted property',
 'flag_review', 'high'),

-- Check for missing insured party (common error)
('insured_party_check', 'entity_exists', 'company', 'companies',
 'For insurance docs, verify the insured party is extracted as a company',
 'flag_review', 'high')
ON CONFLICT DO NOTHING;

-- 6. View for review queue
CREATE OR REPLACE VIEW mrl_review_queue AS
SELECT
    d.id as document_id,
    d.docname,
    d.doccategory,
    d.humndocreviewstatus,
    d.aimatchsummary,
    d.created_at,
    COUNT(DISTINCT vr.id) FILTER (WHERE NOT vr.passed) as validation_failures,
    COUNT(DISTINCT ef.id) as pending_corrections,
    CASE
        WHEN d.humndocreviewstatus = 'pending' THEN 1
        WHEN COUNT(DISTINCT vr.id) FILTER (WHERE NOT vr.passed) > 0 THEN 2
        ELSE 3
    END as priority_order
FROM mrl_documents d
LEFT JOIN mrl_validation_results vr ON d.id = vr.document_id
LEFT JOIN mrl_extraction_feedback ef ON d.id = ef.document_id
WHERE d.humndocreviewstatus IN ('pending', 'needs_review')
   OR EXISTS (SELECT 1 FROM mrl_validation_results WHERE document_id = d.id AND NOT passed)
GROUP BY d.id, d.docname, d.doccategory, d.humndocreviewstatus, d.aimatchsummary, d.created_at
ORDER BY priority_order, d.created_at DESC;

COMMENT ON TABLE mrl_extraction_feedback IS 'Stores human corrections to improve extraction accuracy';
COMMENT ON TABLE mrl_extraction_examples IS 'Few-shot examples for prompt injection';
COMMENT ON TABLE mrl_validation_rules IS 'Automated validation rules for extraction QA';
COMMENT ON TABLE mrl_validation_results IS 'Results of validation checks per document';
