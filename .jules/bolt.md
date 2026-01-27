## 2024-05-23 - Template Variable Naming Mismatch
**Learning:** Verified that accessing a non-existent attribute in a Django template fails silently (returns empty/None). However, this can mask bugs where data is intended to be displayed but isn't. In this case, `beer.average_rating` was used in the template, but the model had no such attribute (only `get_average_rating` method and `avg_rating` annotation). This caused ratings to be hidden.
**Action:** When fixing such issues, always check if an optimized annotation exists (e.g., `avg_rating`) before implementing a method (e.g., `average_rating`) that might introduce N+1 queries. Fixing the template variable to match the annotation fixes the bug AND ensures performance.

## 2024-05-23 - Broken Tests Discovery
**Learning:** The existing test suite (`tests.test_reviews`) is significantly broken due to missing slug generation in the `Beer` model. `Beer.objects.create` does not auto-populate `slug`, causing `IntegrityError` (if unique constraint hits) or `NoReverseMatch` (if used in URLs).
**Action:** Be aware that passing the full test suite might be impossible without fixing out-of-scope bugs. Focus on verifying your specific changes with dedicated tests.
