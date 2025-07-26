# DBR SDK Testing Workflow

## 🎯 Objective
Build, install, and test the DBR SDK locally before updating Phase 5 plans.

## 📋 Prerequisites
- Backend running on `localhost:8000` (for authentication tests)
- Python 3.9+ environment
- UV package manager

## 🔧 Step 1: Build the SDK Package

### Option A: Using UV with Poetry (Recommended)
```bash
# Navigate to SDK directory
cd dbrsdk-python

# Initialize UV environment and install dependencies
uv sync

# Install build tools in the UV environment
uv add --dev build poetry

# Build the package using UV's Python
uv run python -m build

# This creates dist/ directory with wheel and tar.gz files
```

### Option B: Using Poetry directly
```bash
# Navigate to SDK directory
cd dbrsdk-python

# Install Poetry if not available
pip install poetry

# Install dependencies
poetry install

# Build the package
poetry build

# This creates dist/ directory with wheel and tar.gz files
```

### Option C: Direct UV installation (Skip building)
```bash
# Skip building entirely and install directly from source
# This is simpler and works well for local development
```

## 📦 Step 2: Install SDK in Frontend Environment

### Option A: Direct UV Installation (Simplest)
```bash
# Navigate to frontend directory
cd dbr_mvp/frontend

# Install SDK directly from source directory
uv add ../../dbrsdk-python

# Verify installation
uv run python -c "import dbrsdk; print('SDK installed successfully')"
```

### Option B: Install from built wheel (if you built it)
```bash
cd dbr_mvp/frontend

# Install from built wheel (replace version as needed)
uv add ../../dbrsdk-python/dist/dbrsdk-0.2.0-py3-none-any.whl

# Verify installation
uv pip list | grep dbrsdk
```

### Option C: Editable installation for development
```bash
cd dbr_mvp/frontend

# Install in editable mode (changes to SDK reflect immediately)
uv pip install -e ../../dbrsdk-python

# Verify installation
uv run python -c "import dbrsdk; print(dbrsdk.__version__)"
```

## 🧪 Step 3: Run SDK Tests

### Start Backend (Required for Auth Tests)
```bash
# In separate terminal
cd dbr_mvp/backend
uv run python -m dbr.main

# Verify backend is running
curl http://localhost:8000/api/v1/docs
```

### Run Individual Tests
```bash
# From workspace root directory, using frontend's UV environment

# Test 1: Basic SDK functionality
cd dbr_mvp/frontend && uv run python ../../tmp_rovodev_sdk_test_basic.py

# Test 2: Authentication (requires backend)
cd dbr_mvp/frontend && uv run python ../../tmp_rovodev_sdk_test_auth.py

# Test 3: Organization operations (requires backend + auth)
cd dbr_mvp/frontend && uv run python ../../tmp_rovodev_sdk_test_org.py
```

### Run All Tests
```bash
# Run complete test suite from frontend environment
cd dbr_mvp/frontend && uv run python ../../tmp_rovodev_run_all_sdk_tests.py
```

### Alternative: Copy tests to frontend directory
```bash
# Copy test files to frontend directory for easier execution
cp tmp_rovodev_*.py dbr_mvp/frontend/

# Then run from frontend directory
cd dbr_mvp/frontend
uv run python tmp_rovodev_run_all_sdk_tests.py
```

## 📊 Expected Test Results

### ✅ Success Criteria
- **Basic Tests**: SDK imports and initializes correctly
- **Auth Tests**: Can login and get JWT token
- **Org Tests**: Can make authenticated API calls

### ⚠️ Acceptable Partial Failures
- Organization creation may fail if endpoints not available
- Some API calls may fail if no test data exists
- Backend connection failures if backend not running

### ❌ Critical Failures
- SDK import failures (installation problem)
- Authentication completely broken
- No API calls working

## 🔍 Test Files Created

1. **`tmp_rovodev_sdk_test_basic.py`**
   - Tests SDK import and initialization
   - Tests model creation
   - No backend required

2. **`tmp_rovodev_sdk_test_auth.py`**
   - Tests login functionality (sync and async)
   - Tests authenticated client creation
   - Requires backend running

3. **`tmp_rovodev_sdk_test_org.py`**
   - Tests organization-related operations
   - Tests work items and schedules with org context
   - Requires backend + authentication

4. **`tmp_rovodev_run_all_sdk_tests.py`**
   - Runs all tests in sequence
   - Provides comprehensive summary
   - Checks backend status

## 🎯 Success Validation

### Minimum Success Criteria
- [ ] SDK installs without errors
- [ ] Basic import and initialization works
- [ ] Authentication succeeds (with backend running)
- [ ] Can create authenticated client
- [ ] At least one API call succeeds

### Full Success Criteria
- [ ] All basic tests pass
- [ ] Authentication works (sync and async)
- [ ] Authenticated API calls succeed
- [ ] Error handling works correctly
- [ ] SDK models validate properly

## 🚀 Next Steps After Success

1. **Update Phase 5 Plan**
   - Simplify API client implementation
   - Focus on UI/UX instead of API plumbing
   - Leverage SDK models and error handling

2. **Add SDK to Frontend Dependencies**
   ```toml
   # Add to dbr_mvp/frontend/pyproject.toml
   dependencies = [
       "customtkinter>=5.2.0",
       "pillow>=10.0.0", 
       "tk>=0.1.0",
       "dbrsdk>=0.2.0",  # Add this line
   ]
   ```

3. **Create DBR Service Layer**
   - Wrapper around SDK for frontend-specific needs
   - Organization context management
   - UI-friendly error handling

## 🔧 Troubleshooting

### SDK Installation Issues
```bash
# Check Python version
python --version

# Check if SDK directory exists
ls -la dbrsdk-python/

# Try manual installation
cd dbrsdk-python
pip install -e .
```

### Backend Connection Issues
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check backend logs
cd dbr_mvp/backend
uv run python -m dbr.main

# Verify API documentation
open http://localhost:8000/api/v1/docs
```

### Authentication Issues
- Verify default credentials: `admin/admin`
- Check if super user exists in database
- Review backend authentication logs

---

*Run this workflow to validate SDK before updating Phase 5 plans*