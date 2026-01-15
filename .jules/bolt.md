## 2026-01-15 - N+1 Queries in Featured Content
**Learning:** The `home` view's `sponsored_beers` and `featured_beers` were triggering N+1 queries for `Brewery` and `Category` because `select_related` was missing, while the template accessed these relationships. The `latest_reviews` was also missing `beer__brewery` in `select_related`.
**Action:** Always check template usage of related fields when defining QuerySets in views, especially for "featured" or "home" page lists where multiple distinct queries are executed.
