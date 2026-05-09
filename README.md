# Professional Portfolio

For details on this professional portfolio, please see https://ouimet.info (aka https://couimet.github.io).

## Local Development

See more details at https://techfolios.github.io/docs/user-guide/local-development.

Install dependencies:

```bash
rbenv install 3.1.4
rbenv local 3.1.4
bundle install
```

Run the server:

```bash
bundle exec jekyll serve
```

## Deployment

Pushes to `main` are automatically deployed to ouimet.info via `.github/workflows/deploy-ouimet-info.yml` (SSH keypair auth). See the workflow file header for required repository secrets.

The `scripts/sync-ouimet-info.sh` script is kept as a manual recovery tool for rollbacks and direct-from-release syncs.
