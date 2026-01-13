## 2026-03-01 - N+1 Queries on Home Page
**Learning:** The `home` view in `core/views.py` was generating significant N+1 queries. Even though `sponsored_beers` and `featured_beers` were simple queries, the template accessed `beer.brewery.name` and `beer.category.name`, causing a separate query for each beer to fetch the related brewery and category. Additionally, `latest_reviews` was missing a `select_related('beer__brewery')` call, causing further N+1 queries when displaying the brewery name for each review.

**Action:** Always verify what fields are accessed in the template when querying models with foreign keys. Use `select_related` for ForeignKeys and OneToOneFields that are accessed. I used `assertNumQueries` to verify the fix, reducing the query count from ~26 to 5 on the home page.
