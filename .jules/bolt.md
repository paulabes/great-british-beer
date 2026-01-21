## 2025-02-21 - N+1 Query in Django Templates
**Learning:** Accessing related manager counts (e.g., `{{ review.likes.count }}`) in Django templates triggers a separate database query for each iteration in a loop.
**Action:** Always use `annotate()` in the queryset (e.g., `Count('likes', distinct=True)`) and access the annotated attribute in the template (e.g., `{{ review.likes_count }}`) to reduce queries from O(N) to O(1).
