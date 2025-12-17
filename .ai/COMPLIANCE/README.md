# Compliance Framework

This directory contains compliance control mappings for SOC-2 and ISO 27001 audits.

## Overview

The compliance framework maps CI/CD and AI governance controls to regulatory requirements:

| Framework | File | Report |
|-----------|------|--------|
| SOC-2 | `SOC2_MAPPING.yaml` | `reports/SOC2_Control_Matrix.md` |
| ISO 27001 | `ISO27001_MAPPING.yaml` | `reports/ISO27001_Control_Matrix.md` |
| Audit Q&A | `CONTROL_EVIDENCE.yaml` | Generated on demand |

## Files

### SOC2_MAPPING.yaml

Maps controls to SOC-2 Trust Service Criteria:
- **CC6**: Logical and Physical Access Controls
- **CC7**: System Operations
- **CC8**: Change Management

### ISO27001_MAPPING.yaml

Maps controls to ISO 27001:2022 Annex A:
- **A.5**: Organizational Controls
- **A.8**: Technological Controls
- **A.16**: Incident Management

### CONTROL_EVIDENCE.yaml

Pre-written answers to common audit questions with evidence references.

## Usage

### Generate Audit Answers

```bash
# All questions
python scripts/generate_audit_answers.py

# Filter by framework
python scripts/generate_audit_answers.py --framework SOC2
python scripts/generate_audit_answers.py --framework ISO27001

# Output to file
python scripts/generate_audit_answers.py --output audit_answers.md --format markdown

# Show summary
python scripts/generate_audit_answers.py --summary
```

### Export Evidence Package

```bash
# Create evidence ZIP
python scripts/export_compliance_evidence.py

# Custom output path
python scripts/export_compliance_evidence.py --output evidence.zip

# List files (dry run)
python scripts/export_compliance_evidence.py --list
```

### View Control Matrix

- SOC-2: `reports/SOC2_Control_Matrix.md`
- ISO 27001: `reports/ISO27001_Control_Matrix.md`

## Evidence Package Contents

The exported evidence package includes:

1. **AI Governance**
   - `.ai/CLAUDE_RULES.md` - AI behavior contract
   - `.ai/AUTO_MERGE_POLICY.yaml` - Auto-merge policy
   - `.ai/AI_CHANGELOG.md` - Audit trail

2. **Compliance Mappings**
   - Control mapping YAML files
   - Pre-written audit answers

3. **CI/CD Controls**
   - GitHub Actions workflows
   - Configuration files

4. **Access Controls**
   - CODEOWNERS file

5. **Manifest**
   - SHA-256 hashes for integrity verification
   - File metadata and timestamps

## Maintaining Compliance

### Quarterly Review

1. Review control mappings for accuracy
2. Update evidence references if files change
3. Verify audit answers are current
4. Regenerate control matrix reports

### After Significant Changes

1. Update relevant mapping YAML files
2. Add new evidence references
3. Update `CONTROL_EVIDENCE.yaml` if Q&A affected
4. Commit changes with audit trail entry

### Audit Preparation

1. Run `python scripts/export_compliance_evidence.py`
2. Generate audit answers: `python scripts/generate_audit_answers.py --format markdown --output audit_answers.md`
3. Review control matrices
4. Prepare any additional context auditors may need

## Control Coverage

### SOC-2 Coverage

| Criteria | Controls | Status |
|----------|----------|--------|
| CC6.1 | Logical access | Implemented |
| CC6.2 | Authentication | Implemented |
| CC6.3 | Access removal | Implemented |
| CC6.6 | Change management | Implemented |
| CC6.7 | Infrastructure changes | Implemented |
| CC7.1 | Monitoring | Implemented |
| CC7.2 | Incident response | Implemented |
| CC7.3 | Change testing | Implemented |
| CC7.4 | Configuration | Implemented |
| CC8.1 | Change authorization | Implemented |

### ISO 27001 Coverage

| Control | Description | Status |
|---------|-------------|--------|
| A.5.1 | Security policies | Implemented |
| A.5.8 | Project security | Implemented |
| A.5.15 | Access control | Implemented |
| A.8.4 | Source code access | Implemented |
| A.8.8 | Vulnerability mgmt | Implemented |
| A.8.9 | Configuration mgmt | Implemented |
| A.8.25 | Secure SDLC | Implemented |
| A.8.26 | Security requirements | Implemented |
| A.8.27 | Secure architecture | Implemented |
| A.8.28 | Secure coding | Implemented |
| A.8.29 | Security testing | Implemented |
| A.8.31 | Environment separation | Implemented |
| A.8.32 | Change management | Implemented |
| A.16.1 | Incident management | Implemented |

## Questions?

Contact your security team for additional guidance.
