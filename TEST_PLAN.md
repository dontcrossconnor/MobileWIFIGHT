# WiFi Penetration Testing Platform - Test Plan

## Test Framework Status: ✅ COMPLETE

This document outlines the comprehensive test plan for the WiFi Penetration Testing Platform. All tests have been written following TDD principles and are ready for implementation.

## Test Organization

### Directory Structure

```
backend/app/tests/
├── __init__.py
├── conftest.py                    # Pytest fixtures and configuration
├── test_models.py                 # Data model contract tests
├── test_adapter_service.py        # Adapter service tests
├── test_scanner_service.py        # Scanner service tests
├── test_attack_service.py         # Attack service tests
├── test_cracker_service.py        # Cracker service tests
├── test_capture_service.py        # Capture service tests
└── test_report_service.py         # Report service tests
```

## Test Categories

### 1. Contract Tests (test_models.py)

**Purpose**: Validate that all data models conform to immutable contracts

**Test Count**: 20+

**Key Tests**:
- ✅ Network model validation (BSSID format, channel range, signal range)
- ✅ Client model validation (MAC format, immutability)
- ✅ Adapter model validation
- ✅ Attack model validation
- ✅ Cracking model validation
- ✅ Enum value validation
- ✅ Immutability enforcement

**Coverage Target**: 100% (all model fields and validation rules)

### 2. Adapter Service Tests (test_adapter_service.py)

**Purpose**: Test WiFi adapter management functionality

**Test Count**: 15+

**Key Tests**:
- ✅ Detect available adapters
- ✅ Get adapter information
- ✅ Enable/disable monitor mode
- ✅ Set channel
- ✅ Set TX power
- ✅ Validate Alfa AWUS036ACH adapter
- ✅ Error handling (adapter not found, unsupported operations)

**Integration Tests**:
- ⏳ Complete adapter initialization flow
- ⏳ Monitor mode toggle
- ⏳ Channel hopping

**Coverage Target**: 90%+

### 3. Scanner Service Tests (test_scanner_service.py)

**Purpose**: Test network scanning and discovery

**Test Count**: 15+

**Key Tests**:
- ✅ Start scan (passive/active modes)
- ✅ Stop scan
- ✅ Get scan session details
- ✅ Get discovered networks
- ✅ Get specific network by BSSID
- ✅ Get clients (all and filtered by BSSID)
- ✅ Automatic handshake capture detection
- ✅ Error handling (invalid session, adapter not in monitor mode)

**Integration Tests**:
- ⏳ Scan discovers real networks
- ⏳ Channel hopping functionality
- ⏳ Handshake capture on deauth

**Coverage Target**: 90%+

### 4. Attack Service Tests (test_attack_service.py)

**Purpose**: Test attack execution and management

**Test Count**: 20+

**Key Tests**:
- ✅ Create attack
- ✅ Start attack
- ✅ Stop attack
- ✅ Get attack details
- ✅ Get active attacks
- ✅ Validate target
- ✅ Deauth attack captures handshake
- ✅ WPS attack extracts PIN
- ✅ PMKID attack captures PMKID
- ✅ Attack status transitions
- ✅ Error handling (invalid target, attack not found)

**Integration Tests**:
- ⏳ Complete deauth attack flow
- ⏳ WPS Pixie Dust attack
- ⏳ PMKID attack flow

**Coverage Target**: 90%+

### 5. Cracker Service Tests (test_cracker_service.py)

**Purpose**: Test GPU-accelerated password cracking

**Test Count**: 25+

**Key Tests**:
- ✅ Create cracking job
- ✅ Start job (provisions GPU)
- ✅ Stop job (terminates GPU)
- ✅ Get job details
- ✅ Get real-time progress
- ✅ ETA calculation
- ✅ Provision GPU instance
- ✅ Terminate GPU instance
- ✅ Job success (password found)
- ✅ Job exhausted (password not found)
- ✅ Cost tracking
- ✅ GPU selection (best price/performance)
- ✅ Error handling (handshake file not found, provisioning failed)

**Integration Tests**:
- ⏳ Crack with wordlist (requires real GPU)
- ⏳ Crack with mask attack
- ⏳ Crack with rule-based attack

**Coverage Target**: 90%+

### 6. Capture Service Tests (test_capture_service.py)

**Purpose**: Test handshake capture validation and conversion

**Test Count**: 10+

**Key Tests**:
- ✅ Verify valid handshake (returns True)
- ✅ Verify invalid handshake (returns False)
- ✅ Check all 4 EAPOL frames
- ✅ Extract PMKID
- ✅ Convert .cap to .hccapx
- ✅ Convert .cap to hashcat 22000 format
- ✅ Get capture file metadata
- ✅ Error handling (file not found, unsupported format)

**Integration Tests**:
- ⏳ Verify real handshake capture
- ⏳ Extract PMKID from real capture
- ⏳ Format conversion with hcxtools

**Coverage Target**: 90%+

### 7. Report Service Tests (test_report_service.py)

**Purpose**: Test report generation

**Test Count**: 15+

**Key Tests**:
- ✅ Generate report (PDF/HTML/JSON/Markdown)
- ✅ Report includes findings
- ✅ Report includes executive summary
- ✅ Report includes recommendations
- ✅ Get report by ID
- ✅ Export report to file
- ✅ Finding severity levels
- ✅ Finding includes evidence
- ✅ Finding includes remediation
- ✅ Error handling (report not found)

**Integration Tests**:
- ⏳ Generate full PDF report
- ⏳ Report includes charts and graphs
- ⏳ Compliance framework mapping

**Coverage Target**: 80%+

## Test Execution

### Running All Tests

```bash
cd backend
pytest
```

### Running Specific Test Files

```bash
# Model tests
pytest app/tests/test_models.py

# Service tests
pytest app/tests/test_adapter_service.py
pytest app/tests/test_scanner_service.py
pytest app/tests/test_attack_service.py
pytest app/tests/test_cracker_service.py
pytest app/tests/test_capture_service.py
pytest app/tests/test_report_service.py
```

### Running Only Unit Tests (Skip Integration)

```bash
pytest -m "not integration"
```

### Running Only Integration Tests

```bash
pytest -m integration
```

### Running with Coverage

```bash
pytest --cov=app --cov-report=html
# Open htmlcov/index.html to view coverage report
```

### Running Specific Test Classes

```bash
# All adapter contract tests
pytest app/tests/test_adapter_service.py::TestAdapterServiceContract

# Specific test method
pytest app/tests/test_models.py::TestNetworkModel::test_network_creation_valid
```

## Test Fixtures

Located in `conftest.py`, these fixtures provide sample data for all tests:

- `sample_network` - Sample WiFi network
- `sample_client` - Sample client device
- `sample_adapter` - Sample WiFi adapter
- `sample_attack_config` - Sample attack configuration
- `sample_attack` - Sample attack instance
- `sample_attack_result` - Sample attack result
- `sample_cracking_config` - Sample cracking job config
- `sample_gpu_instance` - Sample GPU instance
- `sample_cracking_progress` - Sample cracking progress
- `sample_cracking_job` - Sample cracking job
- `sample_scan_config` - Sample scan configuration
- `sample_scan_session` - Sample scan session

## Current Test Status

**Total Tests Written**: ~150+

**Tests Passing**: 0 (Expected - no implementation yet)

**Tests Failing**: ~150+ (Expected - TDD approach)

**Coverage**: N/A (will be measured after implementation)

## Test-Driven Development Flow

### For Each Service:

1. **Read the tests** - Understand expected behavior
2. **Run tests** - Watch them fail (Red)
3. **Implement minimum code** - Make tests pass (Green)
4. **Refactor** - Improve code while keeping tests passing
5. **Repeat** - Move to next test

### Example: Implementing AdapterService

```bash
# 1. Run adapter service tests (all fail)
pytest app/tests/test_adapter_service.py

# 2. Implement AdapterService class
# File: backend/app/services/adapter.py

# 3. Run tests again (some pass, some fail)
pytest app/tests/test_adapter_service.py -v

# 4. Continue implementing until all pass
# ...

# 5. Check coverage
pytest app/tests/test_adapter_service.py --cov=app.services.adapter --cov-report=term-missing
```

## Integration Test Requirements

Integration tests are currently skipped with `pytest.skip()`. To enable:

1. **System Requirements**:
   - Linux environment
   - WiFi adapter (Alfa AWUS036ACH preferred)
   - Aircrack-ng suite installed
   - hcxtools installed
   - GPU access (for cracking tests)

2. **Test Environment**:
   - Isolated test network
   - No production networks
   - Proper authorization

3. **Enable Integration Tests**:
   ```bash
   # Run integration tests
   pytest -m integration
   
   # Run ALL tests including integration
   pytest
   ```

## Coverage Requirements

### Minimum Coverage Thresholds

- **Unit Tests**: 90%
- **Integration Tests**: 80%
- **Critical Paths**: 100%

### Critical Paths Requiring 100% Coverage

1. Attack target validation
2. Handshake verification
3. GPU cost calculation
4. Adapter mode switching
5. Data model validation

### Measuring Coverage

```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html --cov-fail-under=80

# View coverage
open htmlcov/index.html

# Terminal coverage report
pytest --cov=app --cov-report=term-missing
```

## Continuous Integration

### Pre-commit Checks

```bash
# Run all checks
./scripts/pre-commit.sh  # To be created

# What it runs:
# 1. Black formatting
# 2. Ruff linting
# 3. MyPy type checking
# 4. Pytest with coverage
```

### CI Pipeline (Future)

1. **Lint** - Black, Ruff, MyPy
2. **Test** - Pytest with coverage
3. **Coverage Check** - Enforce thresholds
4. **Type Check** - MyPy strict mode
5. **Security Scan** - Bandit, Safety

## Test Maintenance

### Adding New Tests

1. Follow naming convention: `test_<service>_<method>_<scenario>_<expected_result>`
2. Use appropriate fixtures from `conftest.py`
3. Mock external dependencies
4. Document test purpose with docstring
5. Update this document

### Updating Tests (When Contract Changes)

⚠️ **Contract changes require approval**

If contract changes are approved:
1. Update `CONTRACTS.md`
2. Update models
3. Update ALL affected tests
4. Update fixtures in `conftest.py`
5. Increment version
6. Document migration path

## Performance Testing (Future)

To be added in Phase 5:
- Load testing (concurrent scans)
- Stress testing (long-running attacks)
- GPU utilization benchmarks
- API response time tests

## Security Testing (Future)

To be added in Phase 5:
- Input validation fuzzing
- SQL injection tests
- Command injection tests
- API authentication tests
- Rate limiting tests

## Next Steps

1. ✅ Test framework complete
2. ⏳ Await user direction for implementation
3. ⏳ Implement services (TDD approach)
4. ⏳ Achieve 90%+ coverage
5. ⏳ Enable integration tests
6. ⏳ Add E2E tests

---

**Test Framework Status**: ✅ READY FOR IMPLEMENTATION

All tests are written and waiting for service implementations to make them pass.
