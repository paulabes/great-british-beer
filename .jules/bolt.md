## 2026-01-08 - N+1 Query in Review List
**Learning:** Accessing `review.likes.count` and `review.comments.count` in a loop causes 2N+1 queries. Django's `Count` annotation with `distinct=True` is the proper fix.
**Action:** Use `annotate(like_count=Count('likes', distinct=True), comment_count=Count('comments', distinct=True))` in view and update template to use annotated fields.

## 2026-01-08 - Template Variable Mismatch
**Learning:** The template used `{{ review.comment }}` which doesn't exist (should be `{{ review.content }}`), causing review content to be invisible.
**Action:** Always verify template variable names against model definitions.
