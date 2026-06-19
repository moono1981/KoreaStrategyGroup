Korea Strategy Group — Static site

This folder contains a simple static landing page for `코리아전략그룹`.

Files
- `index.html` — Landing page (dark professional theme, pure HTML/CSS/JS)
- `.nojekyll` — Empty file to allow files/folders starting with underscore on GitHub Pages
- `dashboard.html`, `employees.json`, `projects.json`, etc. — internal project files

Deploy to GitHub Pages (recommended)
1. Create a GitHub repository (e.g., `koreastrategygroup`), then push this folder as the repository root.

   ```bash
   cd D:/Claude_VSCode_20260618/KCG/KoreaStrategyGroup
   git init
   git add .
   git commit -m "Add landing page"
   git branch -M main
   git remote add origin https://github.com/<your-username>/koreastrategygroup.git
   git push -u origin main
   ```

2. On the GitHub repo page: Settings → Pages → Source → `main` branch / `/ (root)` → Save.
3. After a few minutes your site will be available at `https://<your-username>.github.io/koreastrategygroup/`.

Notes
- `.nojekyll` is included to prevent GitHub Pages from ignoring files/folders starting with underscores.
- If you prefer `gh-pages` branch, create that branch and publish from it instead.
- For custom domains, add a `CNAME` file and configure DNS in GitHub Pages settings.
