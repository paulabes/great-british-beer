## 2024-05-24 - [N+1 Query in Django Templates]
**Learning:** Accessing related object counts in a loop (e.g. `review.likes.count`) triggers a separate query for each item. Django's `annotate(count=Count('related'))` is the standard fix. Also learned that `whitenoise` static file serving can interfere with `assertContains` if not configured for tests, though here it was a template logic bug.
**Action:** Always check template loops for method calls that hit the database. Use `django-debug-toolbar` or `reset_queries()` in tests to verify query counts.
