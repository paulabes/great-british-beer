## 2024-05-23 - Count Annotation Cartesian Product
**Learning:** When annotating multiple `Count` aggregations on different related fields (e.g., `likes` and `comments`) on the same queryset, you MUST use `distinct=True` (e.g., `Count('likes', distinct=True)`). Without it, the joins multiply the rows, resulting in inflated, incorrect counts (Cartesian product).
**Action:** Always check for potential Cartesian products when using multiple annotations involving joins. Verify with `distinct=True`.
