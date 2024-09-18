@echo off
setlocal enabledelayedexpansion

REM This script automates the process of generating merged Portainer templates,
REM and optionally committing the changes and pushing them to GitHub.
REM It requires a conda environment named 'aider' and assumes you're in a git repository.

REM Check for --commit flag
set COMMIT_CHANGES=0
for %%a in (%*) do (
    if "%%a"=="--commit" set COMMIT_CHANGES=1
)

REM Activate conda environment
call conda activate aider || (
    echo Failed to activate conda environment 'aider'. Please make sure it exists.
    exit /b 1
)

REM Run the Python script
python portainer_templates_generate.py
if !errorlevel! neq 0 (
    echo Failed to run portainer_templates_generate.py
    echo Python script output:
    python portainer_templates_generate.py
    exit /b !errorlevel!
)

if %COMMIT_CHANGES%==1 (
    REM Git operations
    git add releases\templates.json
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
) else (
    echo Merged templates have been updated. Use --commit flag to commit and push changes.
)
