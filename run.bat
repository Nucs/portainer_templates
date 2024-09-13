@echo off
conda activate aider
python portainer_download_and_merge.py -o merged_templates.json
git add merged_templates.json
git commit -m "Update merged_templates.json"
git push
echo Merged templates have been updated and pushed to GitHub.
