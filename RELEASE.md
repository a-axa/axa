# Release process

## Publishing `axa.skill`

From the repository parent directory:

```sh
rm -f axa/axa.skill
zip -qr axa/axa.skill axa \
  -x 'axa/.git/*' \
     'axa/axa.skill' \
     'axa/RELEASE.md'

python3 axa/tools/validate-release.py
```

Inspect the final diff and archive listing before publishing.

## GitHub Release Flow

1. Update `CHANGELOG.md`: move items from `[Unreleased]` into a new version section with today's date.
2. Commit the changelog on `main`.
3. Tag and push the release:

   ```sh
   git tag v0.1.0
   git push origin v0.1.0
   ```

4. On GitHub, create a Release from the tag and paste the changelog section as the release notes.

Use semantic versioning: MAJOR for breaking workflow changes, MINOR for new agents or stages, PATCH for prompt fixes and clarifications.
