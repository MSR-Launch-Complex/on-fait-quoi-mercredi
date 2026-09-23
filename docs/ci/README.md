# The two workflows, waiting to be installed

`.bureau.yml` lists `.github/workflows` under `forbidden_paths`, and an agent of the
Bureau corps may not write there. Slice 1 needs CI all the same: the issue asks for the
tests to run on every pull request, and for the site to be published from `main`. So the
two workflows are written and reviewable here, and a person installs them:

```sh
mkdir -p .github/workflows
cp docs/ci/test.yml   .github/workflows/test.yml
cp docs/ci/deploy.yml .github/workflows/deploy.yml
```

Then, once: **Settings → Pages → Build and deployment → Source: GitHub Actions**.

Until that is done, `make test` still runs locally and is what `.bureau.yml` declares as
`test_command`; what is missing is the automatic run on a pull request and the automatic
publish on merge.

Either move these two files into place, or drop `.github/workflows` from
`forbidden_paths` so the next agent can. Leaving both as they are means CI never runs.
