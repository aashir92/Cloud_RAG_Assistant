param(
    [string]$Branch = "main"
)

$ErrorActionPreference = "Stop"

$hfRemoteUrl = "https://huggingface.co/spaces/Aashir92/Cloud_RAG_Assistant"
$ghRemoteUrl = "https://github.com/aashir92/Cloud_RAG_Assistant"

Write-Host "Preparing git repository in task4..." -ForegroundColor Cyan

if (-not (Test-Path ".git")) {
    git init
}

if (-not (git config user.name 2>$null)) {
    Write-Host "Git user.name is not configured. Configure git identity before running this script." -ForegroundColor Red
    exit 1
}

if (-not (git config user.email 2>$null)) {
    Write-Host "Git user.email is not configured. Configure git identity before running this script." -ForegroundColor Red
    exit 1
}

git checkout -B $Branch
git add .

if (-not (git diff --cached --quiet)) {
    git commit -m "Set up deployable Streamlit RAG app for Hugging Face Spaces and GitHub"
} else {
    Write-Host "No new changes to commit." -ForegroundColor Yellow
}

$existingRemotes = git remote
if ($existingRemotes -contains "hf") {
    git remote set-url hf $hfRemoteUrl
} else {
    git remote add hf $hfRemoteUrl
}

if ($existingRemotes -contains "origin") {
    git remote set-url origin $ghRemoteUrl
} else {
    git remote add origin $ghRemoteUrl
}

Write-Host "Pushing to Hugging Face Space..." -ForegroundColor Cyan
git push -u hf $Branch

Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
git push -u origin $Branch

Write-Host "Done. Repository pushed to both remotes." -ForegroundColor Green
