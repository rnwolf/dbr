# Known Issues - DBR MVP Backend

This document tracks known issues and bugs that need to be investigated and resolved.

## 🐛 Active Issues

### Issue #1: Work Item Task Update API Not Persisting Changes
**Status:** Resolved  
**Priority:** Medium  
**Component:** Work Item API (`/api/v1/workitems/{id}/tasks/{task_id}`)  
**Date Reported:** 2025-07-20  
**Date Resolved:** 2025-08-01

**Description:**
The individual task update endpoint `PUT /api/v1/workitems/{work_item_id}/tasks/{task_id}` was not properly persisting task completion status changes to the database. When updating a task's `completed` status from `false` to `true`, the change was not reflected in the work item's progress calculation.

**Resolution:**
The issue was resolved by ensuring that the `tasks` field of the `WorkItem` object was explicitly marked as modified. This was achieved by re-assigning the `tasks` list to itself after modification, which signals to SQLAlchemy that the JSON field has been updated. The fix was verified by running the `test_work_item_tasks_api` test.

**Expected Behavior:**
- Update task completion status via API
- Task change should be persisted to database
- Work item progress percentage should recalculate correctly
- Example: 3 tasks with 1 completed → update 1 more → should show 66.67% progress

**Actual Behavior:**
- Task update API returns 200 OK
- Task data appears updated in response
- But progress percentage remains unchanged (33.33% instead of 66.67%)
- No UPDATE SQL query visible in logs for task update operation

**Test Case:**
```python
# In tests/test_api/test_work_items.py::test_work_item_tasks_api
# This specific assertion fails:
assert updated_work_item["progress_percentage"] == 66.67  # 2 out of 3 completed
```

**Investigation Notes:**
1. **Task Creation Works:** Initial task creation via work item update works correctly
2. **SQL Logs:** Task creation shows proper UPDATE query, but task update doesn't
3. **Session Handling:** Tried various session refresh/commit strategies
4. **JSON Field Mutation:** Attempted multiple approaches to force SQLAlchemy change detection:
   - `work_item.tasks = work_item.tasks.copy()`
   - `work_item.tasks = list(work_item.tasks)`
   - Direct task dictionary modification
5. **Type Conversion:** Added integer conversion for task ID comparison
6. **Database Refresh:** Tried fresh database queries after update

**Potential Root Causes:**
- SQLAlchemy JSON field mutation detection issue
- Session isolation between API endpoints
- Task finding logic not working correctly
- FastAPI dependency injection session handling

**Workaround:**
Use the main work item update endpoint (`PUT /api/v1/workitems/{id}`) to update entire tasks array instead of individual task updates.

**Related Files:**
- `src/dbr/api/work_items.py` - `update_work_item_task()` function
- `tests/test_api/test_work_items.py` - `test_work_item_tasks_api()` test
- `src/dbr/models/work_item.py` - `calculate_progress()` method

**Impact:**
- **Low Impact:** Core work item functionality works
- **5 out of 6 API tests passing** (83% success rate)
- Main DBR features (schedules, time progression) not affected
- Task management via main work item update still functional

---

## 📋 Issue Investigation Checklist

When investigating this issue:

- [ ] Check SQLAlchemy JSON field change detection patterns
- [ ] Verify FastAPI session dependency lifecycle
- [ ] Test with direct SQLAlchemy session (bypass FastAPI)
- [ ] Add debug logging to task update endpoint
- [ ] Compare working task creation vs failing task update code paths
- [ ] Test with different SQLAlchemy JSON field mutation approaches
- [ ] Consider using SQLAlchemy's `flag_modified()` for JSON fields

## 🔄 Future Improvements

Once resolved, consider:
- Adding comprehensive task management API tests
- Implementing task history/audit trail
- Adding task assignment and due dates
- Bulk task operations API

---

*Last Updated: 2025-07-20*
*Next Review: When implementing task management enhancements*