# GitHub Setup

The repository is public at:

```text
git@github.com:worktemp-coder/secureapp-platform.git
```

The public setting is needed for code scanning and SARIF uploads.

## Push access

The current remote uses SSH. If the key is already on GitHub, this is enough:

```bash
ssh -T git@github.com
git push -u origin main
```

If you need a new key:

```bash
ssh-keygen -t ed25519 -C "you@example.com"
cat ~/.ssh/id_ed25519.pub
```

Add the public key at <https://github.com/settings/ssh/new>, then test it:

```bash
ssh -T git@github.com
```

For HTTPS instead, authenticate with the GitHub CLI and change the remote:

```bash
gh auth login
gh auth setup-git
git remote set-url origin https://github.com/worktemp-coder/secureapp-platform.git
```

## Commit and push main

```bash
git status
git diff --stat
git add -A
git commit -m "feat: build secureapp platform"
git push -u origin main
```

Before committing, check that `deploy/k8s/secret.yaml` does not appear in `git status`. It is gitignored and should stay out of the repository.

## Create the production branch

After `main` is pushed:

```bash
git switch -c prod
git push -u origin prod
git switch main
```

The CI workflow runs on both branches. The `deploy-smoke` job runs only on pushes to `main` or `prod`.

## Protect main and prod

In **Settings > Branches**, add a branch protection rule or ruleset for `main` and `prod`:

- Require a pull request before merging.
- Require status checks to pass.
- Require branches to be up to date before merging.
- Block force pushes and deletions.

Require these checks:

- `Test and lint`
- `Secret scan`
- `SAST`
- `Dependency audit`
- `Build and scan image`
- `Validate monitoring manifests`

Do not require `Deploy smoke test` for pull requests. That job is limited to pushes to `main` and `prod`.

## Check the pipeline

Open **Actions > CI** after the push. A normal run should show:

```text
Test and lint
Secret scan
SAST
Dependency audit
Build and scan image
Deploy smoke test
Validate monitoring manifests
```

A tag push also runs `Release image artifact`:

```bash
git switch main
git pull
git tag -a v1.0.0 -m "SecureApp Platform v1.0.0"
git push origin v1.0.0
```

The release should contain:

- `secureapp-image.tar.gz`
- `sbom.cdx.json`
- `trivy-image.sarif`
- `sha256sums.txt`

## Screenshots

The list of screenshots and the demo steps are in [DEMO.md](DEMO.md). Put the images in `docs/screenshots/`.
