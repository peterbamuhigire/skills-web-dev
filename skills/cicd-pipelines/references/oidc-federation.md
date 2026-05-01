# OIDC Federation From GitHub Actions

GitHub Actions issues a short-lived OIDC token per workflow run when the job sets `permissions: id-token: write`. The token is exchanged at the cloud (or Vault) trust boundary for a short-lived credential — no long-lived secret ever lives in the repo.

The OIDC subject (`sub`) claim encodes `repo:<owner>/<repo>:ref:refs/heads/<branch>` (or `:environment:<env>`). Bind the trust policy to the exact subject — never `repo:*` — to prevent a fork from assuming the role.

## OIDC to AWS IAM

Trust policy on the IAM role (`github-actions-deploy`):

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com" },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
        "token.actions.githubusercontent.com:sub": "repo:acme/api:environment:production"
      }
    }
  }]
}
```

Workflow:

```yaml
permissions: { id-token: write, contents: read }
steps:
  - uses: actions/checkout@v4
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789012:role/github-actions-deploy
      aws-region: eu-west-1
  - run: aws sts get-caller-identity
```

## OIDC to GCP Workload Identity Federation

```yaml
permissions: { id-token: write, contents: read }
steps:
  - uses: google-github-actions/auth@v2
    with:
      workload_identity_provider: projects/123/locations/global/workloadIdentityPools/gh/providers/gh-oidc
      service_account: deploy@project.iam.gserviceaccount.com
  - uses: google-github-actions/setup-gcloud@v2
  - run: gcloud auth list
```

Bind the WIF provider attribute condition: `assertion.repository == 'acme/api' && assertion.ref == 'refs/heads/main'`.

## OIDC to HashiCorp Vault (JWT auth)

Vault server-side config lives in `cicd-devsecops`. From the workflow:

```yaml
permissions: { id-token: write, contents: read }
steps:
  - uses: hashicorp/vault-action@v3
    with:
      url: https://vault.example.com:8200
      method: jwt
      role: github-actions-acme-api
      jwtGithubAudience: https://github.com/acme
      secrets: |
        kv/data/api/prod db_password | DB_PASSWORD ;
        kv/data/api/prod jwt_signing | JWT_SIGNING_KEY
  - run: deploy.sh
```

The Vault role binds `bound_claims.sub = repo:acme/api:environment:production` and a short `token_ttl` (15 minutes is the rule of thumb).

## Anti-patterns

- Using `repo:owner/*` or only matching `aud` — any branch (or fork PR) can assume the role.
- Granting the role write access to the whole account — scope to one ECR repo, one ECS service, one SSM path.
- Storing the resulting credentials as a step output or env var that gets logged.
- Mixing static `AWS_ACCESS_KEY_ID` with OIDC in the same workflow — the static key wins and defeats the federation story.
