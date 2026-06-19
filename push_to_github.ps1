# Run this in PowerShell on your machine to push the repo to GitHub
# Make sure Git is installed and you've created a PAT or have gh auth configured.

Set-Location -Path "D:\\Claude_VSCode_20260618\\KCG\\KoreaStrategyGroup"

# Configure identity if not set
# git config --global user.name "Your Name"
# git config --global user.email "you@example.com"

git init
git add .
git commit -m "Initial commit: KoreaStrategyGroup"
git branch -M main
git remote add origin https://github.com/moono1981/KoreaStrategyGroup.git

# This will prompt for credentials. Use username: moono1981 and password: <YOUR_PAT>
git push -u origin main

# Alternatively, create the repo and push in one step with GitHub CLI (gh):
# gh auth login
# gh repo create moono1981/KoreaStrategyGroup --public --source=. --remote=origin --push
