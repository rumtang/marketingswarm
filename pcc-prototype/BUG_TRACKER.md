# PCC Prototype Bug Tracker

## 🐛 Active Bugs

### Critical (P0)

#### Bug ID: BUG-001
**Priority**: P0
**Component**: Backend
**Status**: Fixed

**Description**: 
Backend application fails to complete startup. The narrative engine starts generating events during the lifespan startup, blocking the FastAPI application from becoming ready to serve HTTP requests.

**Steps to Reproduce**:
1. Run `docker-compose up`
2. Wait for services to start
3. Try to access http://localhost:8000/health
4. Connection is refused/reset

**Expected Behavior**:
- Application should start up and be ready to serve requests
- Health endpoint should return 200 OK
- Narrative engine should start after app is ready

**Actual Behavior**:
- Application gets stuck in startup phase
- Narrative engine continuously generates events during startup
- HTTP endpoints are not accessible
- Health checks fail

**Error Messages**:
```
curl: (56) Recv failure: Connection reset by peer
```

**Root Cause**:
The narrative engine's `start()` method is called in `get_narrative_engine()` which is invoked during the FastAPI lifespan startup. The `_populate_initial_patients()` method generates many LLM calls synchronously, blocking the event loop.

**Fix**:
Move the narrative engine initialization to run in the background after app startup completes.

**Fix Applied**:
1. Modified `get_narrative_engine()` to not start the engine immediately
2. Added background task in lifespan to start narrative engine after 2 second delay
3. Fixed health check to properly check narrative engine's database connection
4. Updated health endpoint to handle "starting" state gracefully

**Verified**: Yes
**Verification Date**: 2025-01-13

### High (P1)

#### Bug ID: BUG-002
**Priority**: P1
**Component**: Backend
**Status**: Fixed

**Description**: 
API endpoint /api/bed-status returns Internal Server Error due to database client not being initialized.

**Steps to Reproduce**:
1. Get auth token: `curl -X POST http://localhost:8000/token -d "username=admin&password=admin123"`
2. Call bed-status endpoint with token
3. Receive 500 Internal Server Error

**Expected Behavior**:
Should return list of bed status

**Actual Behavior**:
500 Internal Server Error

**Error Messages**:
```
AttributeError: 'NoneType' object has no attribute 'execute'
```

**Root Cause**:
The global `db_client` is never initialized. The narrative engine has its own database client.

**Fix Applied**:
Updated all endpoints to use `narrative_engine.db` instead of the global `db_client`.

**Verified**: Yes
**Verification Date**: 2025-01-13

---

#### Bug ID: BUG-003
**Priority**: P1
**Component**: Backend
**Status**: Fixed

**Description**: 
HL7Consumer missing consume_message method causing continuous errors in background task.

**Error Messages**:
```
ERROR:main:Error processing narrative event: 'HL7Consumer' object has no attribute 'consume_message'
```

**Root Cause**:
The HL7Consumer class doesn't have the expected consume_message method.

**Fix Applied**:
1. Changed from `consume_message` to `consume_events` which returns a list
2. Updated code to iterate over the list of events
3. Fixed DatabaseClient call from `process_event` to `get_bed_status`

**Verified**: Yes
**Verification Date**: 2025-01-13

### Medium (P2)

#### Bug ID: BUG-004
**Priority**: P2
**Component**: Backend
**Status**: Fixed

**Description**: 
API endpoint /api/bed-status times out due to excessive LLM calls when enriching patient data.

**Steps to Reproduce**:
1. Call the /api/bed-status endpoint
2. Request times out after 2+ minutes

**Expected Behavior**:
Should return bed status quickly (<1 second)

**Actual Behavior**:
Request times out

**Root Cause**:
The endpoint calls `narrative_engine.get_patient_data()` for each patient, which makes an LLM call every time. With many beds occupied, this creates dozens of sequential LLM calls.

**Suggested Fix**:
Cache patient data in the narrative engine to avoid repeated LLM calls.

**Fix Applied**:
1. Created cache.py module with in-memory caching (patient and API caches)
2. Updated narrative engine to use patient cache with 5-minute TTL
3. Implemented batch patient retrieval in narrative engine
4. Modified /api/bed-status to use batch loading and 30-second API cache
5. Added tiered model selection (nano/mini/full) to reduce LLM costs

**Performance Results**:
- First call: ~18ms (down from timeout)
- Cached calls: ~12ms
- Cache effectiveness verified

**Verified**: Yes
**Verification Date**: 2025-01-13

### Low (P3)
None yet - testing in progress

## 🧪 Test Plan

### 1. Service Startup Tests
- [ ] All Docker services start successfully
- [ ] No errors in docker-compose up
- [ ] Backend connects to Kafka
- [ ] Frontend builds without errors
- [ ] WebSocket connection established

### 2. API Tests
- [ ] Health endpoint returns 200
- [ ] Authentication works with demo credentials
- [ ] Protected endpoints require auth
- [ ] WebSocket accepts connections
- [ ] Bed status updates received

### 3. Narrative Engine Tests
- [ ] Initial patients generated
- [ ] Patient stories are coherent
- [ ] Events generated at natural pace
- [ ] Fallback templates work
- [ ] Session persistence works

### 4. UI/UX Tests
- [ ] Dashboard loads without errors
- [ ] Real-time updates display
- [ ] No React errors in console
- [ ] Error boundaries catch issues
- [ ] WebSocket reconnection works

### 5. Agent Tests
- [ ] Capacity Predictor responds
- [ ] Discharge Accelerator works
- [ ] Concierge Chat functions
- [ ] All agents use narrative context

### 6. Stability Tests
- [ ] 60-minute continuous operation
- [ ] No memory leaks
- [ ] No duplicate patients
- [ ] Consistent performance
- [ ] Graceful error recovery

## 📊 Test Results

### Test Run: 2025-01-13
- **Tester**: Claude
- **Version**: 0.2.0
- **Environment**: Docker Compose

#### Results:

##### ✅ Completed Tests:
1. **Service Startup** - All services start successfully after fixing startup blocking issue
2. **Health Endpoint** - Returns healthy status for all services
3. **Authentication** - JWT authentication works with demo credentials

##### ❌ Failed Tests:
1. **API Performance** - /api/bed-status endpoint times out due to excessive LLM calls (BUG-004)

##### ⏸️ Pending Tests:
1. **WebSocket Connection** - Not tested yet
2. **Narrative Engine** - Generating patients but performance issues
3. **UI Functionality** - Frontend serving but not fully tested
4. **Agent Functionality** - Not tested yet
5. **60-minute Stability** - Cannot test until performance issues resolved

## 🔧 Fixed Bugs

### Version 0.2.0
- ✅ CSS border-border error - Fixed in tailwind.config.js
- ✅ Duplicate files - Already removed
- ✅ Demo mode flags - Removed from frontend
- ✅ Data generator service - Removed from docker-compose

## 📝 Bug Template

### Bug ID: BUG-XXX
**Priority**: P0/P1/P2/P3
**Component**: Backend/Frontend/Infrastructure
**Status**: New/In Progress/Fixed/Won't Fix

**Description**: 
Brief description of the issue

**Steps to Reproduce**:
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior**:
What should happen

**Actual Behavior**:
What actually happens

**Error Messages**:
```
Any error messages or logs
```

**Fix**:
Description of the fix applied

**Verified**: Yes/No
**Verification Date**: YYYY-MM-DD