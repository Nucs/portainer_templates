@echo off
setlocal enabledelayedexpansion

REM Activate conda environment
call conda activate aider || (
    echo Failed to activate conda environment 'aider'. Please make sure it exists.
    exit /b 1
)

REM Run the Python script
python portainer_templates_generate.py -o merged_templates.json
if !errorlevel! neq 0 (
    echo Failed to run portainer_templates_generate.py
    exit /b !errorlevel!
)

REM Git operations
git add merged_templates.json
git commit -m "Update merged_templates.json"
if !errorlevel! neq 0 (
    echo Failed to commit changes. There might be no changes or a git error occurred.
    exit /b !errorlevel!
)

REM Check if there's a remote named 'origin'
git remote get-url origin >nul 2>&1
if !errorlevel! neq 0 (
    echo No 'origin' remote found. Please set up a remote repository using:
    echo git remote add origin ^<repository-url^>
    exit /b 1
)

REM Try to push to the current branch
for /f "tokens=*" %%i in ('git rev-parse --abbrev-ref HEAD') do set current_branch=%%i
git push origin !current_branch!
if !errorlevel! neq 0 (
    echo Failed to push changes to GitHub. Please check your internet connection and git configuration.
    echo You can manually push changes using: git push origin !current_branch!
    exit /b !errorlevel!
)

echo Merged templates have been updated and pushed to GitHub successfully.
