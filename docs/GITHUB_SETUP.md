# GitHub Setup

The repository is intended to be public at:

```text
git@github.com:worktemp-coder/secureapp-platform.git
```

The assistant creates files only; the repository owner performs authentication, commits, pushes, branch protection, and screenshots.

## 1. Authenticate and Set Identity

Use GitHub CLI with HTTPS credentials:

```bash
gh auth login
gh auth setup-git
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git remote set-url origin https://github.com/worktemp-coder/secureapp-platform.git
```

Alternatively, keep SSH and upload a key:

```bash
ssh-keygen -t ed25519 -C "you@example.com"
gh ssh-key add ~/.ssh/id_ed25519.pub
ssh -T git@github.com
```

If the repository does not exist yet:

```bash
gh repo create worktemp-coder/secureapp-platform --public --source=. --remote=origin
```

Do not use `--push` until the files are reviewed and committed.

## 2. Commit and Push Main

```bash
git status
git diff --stat
git add -A
git commit -m "feat: build secureapp platform"
git push -u origin main
```

The public repository is required for SARIF upload and GitHub code scanning.

## 3. Create the Production Branch

After the first successful `main` push:

```bash
git switch -c prod
git push -u origin prod
```

CI runs on both `main` and `prod`. The `deploy-smoke` job runs on pushes to either branch.

## 4. Protect Main and Prod

In **Settings > Branches**, add a branch protection rule (or ruleset) for `main` and `prod`:

- Require a pull request before merging.
- Require status checks to pass.
- Require branches to be up to date before merging.
- Block force pushes and deletions.

Require these check names:

- `Test and lint`
- `Secret scan`
- `SAST`
- `Dependency audit`
- `Build and scan image`
- `Validate monitoring manifests`

Do not require `Deploy smoke test` for pull requests: that job is intentionally limited to pushes to `main` and `prod`.

## 5. Verify the Pipeline

Open **Actions > CI** after the push. The expected jobs are:

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

## 6. Capture Evidence

Follow [DEMO.md](DEMO.md) for the local and GitHub screenshot checklist. Store images in `docs/screenshots/` using the listed filenames.
