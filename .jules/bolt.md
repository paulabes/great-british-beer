## 2024-05-23 - [Django N+1 and Redundant Counts]
**Learning:**
1.  **Redundant Counts:** When using `Paginator`, `page_obj.paginator.count` is already calculated (and cached). Calling `queryset.count()` again for "Total items" context variables triggers a redundant `SELECT COUNT(*)` query.
2.  **N+1 in Lists:** Displaying related counts (like likes/comments on a review) in a loop causes N+1 queries. Django's `.annotate(count=Count('related_field', distinct=True))` solves this efficiently.
3.  **Template Access:** Accessing a ManyToMany or Reverse ForeignKey manager in a template (e.g. `review.likes.count`) triggers a query if not annotated or prefetched. If annotated, use the annotation name (e.g. `review.likes_count`).

**Action:**
- Always check `page_obj.paginator.count` before adding a manual count to context.
- Use `assertNumQueries` to verify query counts in list views.
- Annotate counts for related objects when displaying them in lists.
