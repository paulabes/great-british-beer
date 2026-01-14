## 2024-05-23 - Homepage N+1 Queries & Sliced QuerySet Pitfalls
**Learning:** Sliced querysets in Django (e.g., `queryset[:3]`) are not cached. Accessing them multiple times (e.g., `if queryset.exists():` then iterating) triggers multiple DB queries.
**Action:** When dealing with small sliced querysets that need to be checked and iterated, evaluate them to a list immediately (`list(queryset)`) to ensure a single DB hit. Also, always check for N+1 queries when accessing related fields (like `brewery` on `Beer`) in templates.
