## 2024-05-22 - Optimizing Django Review List with Annotations
**Learning:** When using Django's `Count` aggregation on multiple related fields (e.g., counting likes AND comments for the same object), you MUST use `distinct=True`. Otherwise, you get a Cartesian product explosion, resulting in incorrect counts (e.g., 2 likes * 3 comments = 6 likes reported).
**Action:** Always verify generated SQL or counts when annotating multiple relationships. Use `Count('field', distinct=True)`.

## 2024-05-22 - Avoiding Redundant Count Queries
**Learning:** `queryset.count()` always executes a database query. When using `Paginator`, `page_obj.paginator.count` is already calculated and cached.
**Action:** Use `page_obj.paginator.count` in templates/views instead of calling `.count()` on the queryset again.
