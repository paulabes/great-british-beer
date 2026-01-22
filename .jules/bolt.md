## 2024-05-22 - Optimizing `review_detail` View
**Learning:** `get_object_or_404` accepts a `QuerySet` as the first argument, not just a `Model` class. This allows applying `select_related` and `prefetch_related` *before* the object is retrieved, solving N+1 issues on the detail object itself.
**Action:** When using `get_object_or_404`, always check if the template accesses related fields (foreign keys). If so, pass `Model.objects.select_related(...)` instead of `Model`.

**Learning:** Iterating over reverse relationships in templates (e.g., `{% for x in obj.related_set.all|slice:":3" %}`) often causes hidden performance issues because it triggers a fresh query, and if you access related fields on *those* objects (like `x.user`), it causes N+1.
**Action:** Pre-fetch "sidebar" or "related" lists in the view, apply optimizations like `select_related` to them, and pass them as explicit context variables (e.g., `other_reviews`). This gives full control over the query and avoids template-induced N+1s.
