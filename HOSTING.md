# Publish FINN from your personal GitHub account

The project in this directory is local-only and has no Git remote. The phone demo is the static `dist/` folder. It runs on GitHub Pages without a server. Live lookup of an arbitrary NSE ticker uses the local Python server and is not available on GitHub Pages.

1. Sign in to **your personal GitHub account** and create a new **public, empty** repository named `finn-investor-desk`. Do not add a README or license during creation.
2. In this directory, run the smoke test and publish `main`:

   ```bash
   cd ~/nipun/finn
   python3 tests/smoke.py
   git add -A
   git commit -m "Prepare personal GitHub hosting"
   git remote add origin https://github.com/YOUR_USERNAME/finn-investor-desk.git
   git push -u origin main
   ```

   This stages the removal of the old private Site identity as well as the updated documentation. Replace `YOUR_USERNAME` with your account name. If Git reports there is nothing to commit, continue.

3. Publish only the static app on a `gh-pages` branch:

   ```bash
   git subtree split --prefix dist -b gh-pages
   git push -u origin gh-pages
   ```

4. In the GitHub repository, open **Settings → Pages**. Under **Build and deployment**, choose **Deploy from a branch**, select **gh-pages** and **/(root)**, then save. The demo URL will be `https://YOUR_USERNAME.github.io/finn-investor-desk/`. Wait for Pages to show a successful deployment, then open the URL on your phone.
5. Replace the two placeholders in `COVERING_NOTE.md` with your actual links before sending it.

For later app updates, commit the changes on `main`, push `main`, then run:

```bash
git branch -D gh-pages
git subtree split --prefix dist -b gh-pages
git push origin gh-pages
```

GitHub Pages may reject the last push as non-fast-forward after a subtree rebuild. If that happens, use `git push --force-with-lease origin gh-pages` only for the generated `gh-pages` branch; do not force-push `main`.
