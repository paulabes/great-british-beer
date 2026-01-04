## 2024-05-23 - N+1 Query Optimization in Django
**Learning:** Using `count` in Django templates on a related manager (e.g., `review.likes.count`) triggers a separate database query for each iteration of the loop. This causes N+1 performance issues.
**Action:** Use `annotate` with `Count` in the view to pre-calculate these values. When annotating multiple related fields, ensure to use `distinct=True` (e.g., `Count('likes', distinct=True)`) to avoid incorrect counts due to Cartesian products.
