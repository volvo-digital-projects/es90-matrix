# ES90 Matrix: canonical development and production mirror

- Canonical checkout: C:/Users/User/Projects/Volvo-Digital-Projects/es90-matrix
- Canonical private origin: https://github.com/volvo-digital-projects/es90-matrix.git
- Implement all future application changes here. Validate the intended changes, commit only reviewed non-secret source, push to this origin and verify the remote SHA.
- Production mirror: https://github.com/volvo-es90-matrix/es90-matrix
- Public URL (must not change): https://volvo-es90-matrix.github.io/es90-matrix/
- The production mirror exists only to preserve the public URL and run credentials that have not yet been migrated. Do not develop application changes directly in it.
- Before every production deployment, fetch the production mirror and integrate newer generated reservation, charger, subsidy, competitor-price, TMAP, CDSID and version data into this canonical repository. Never force-push or overwrite newer production data.
- The `Publish production mirror` workflow deploys each validated canonical `main` commit to the production mirror with a fast-forward-only push. If production has a newer commit, integrate it here first; never bypass the guard with a force-push.
- After deployment, wait for the production Pages build and verify the live URL.
- GitHub Actions and secrets remain active in the production mirror until their credentials and schedules are deliberately migrated. Keep Actions and Pages disabled in the private canonical repository unless the user explicitly approves that infrastructure change.
- Reference-only local original: C:/Users/User/OneDrive/문서/ES90 경쟁력 분석 도구앱_v1
- Private local preservation copies: C:/Users/User/Projects/Volvo-Digital-Projects/local-only-archive/es90-matrix
- Do not commit local secrets or raw backup directories. Do not delete original folders without a full backup audit and explicit cleanup approval.
