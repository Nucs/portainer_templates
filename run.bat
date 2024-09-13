@echo off
setlocal enabledelayedexpansion

REM Activate conda environment
call conda activate aider || (
    echo Failed to activate conda environment 'aider'. Please make sure it exists.
    exit /b 1
)

REM Run the Python script
python portainer_download_and_merge.py -o merged_templates.json
if !errorlevel! neq 0 (
    echo Failed to run portainer_download_and_merge.py
    exit /b !errorlevel!
)

REM Git operations
git add merged_templates.json
git commit -m "Update merged_templates.json"
if !errorlevel! neq 0 (
    echo Failed to commit changes. There might be no changes or a git error occurred.
    exit /b !errorlevel!
)

git push
if !errorlevel! neq 0 (
    echo Failed to push changes to GitHub. Please check your internet connection and git configuration.
    exit /b !errorlevel!
)

echo Merged templates have been updated and pushed to GitHub successfully.
