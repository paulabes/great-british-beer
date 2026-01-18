## 2024-05-23 - Template Field Mismatch & N+1 Queries
**Learning:** Found that `review_list.html` was trying to access `review.comment` instead of `review.content`, causing reviews to appear empty. This highlights the importance of checking templates against models, especially when field names might be ambiguous (comment vs content). Also, `review.title` was missing.
**Action:** Always verify template rendering with actual data, and cross-reference model field names. When optimizing, if you see missing data in tests, it might be a real bug.

## 2024-05-23 - Test Data Setup
**Learning:** `create` method in tests for ForeignKeys needs model instances, not strings. Django doesn't auto-fetch or create FKs from strings in `create()`.
**Action:** Ensure test setup creates dependencies (Brewery, Category) before creating the main object (Beer).
