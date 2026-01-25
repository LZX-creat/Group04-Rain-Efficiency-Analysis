#!/bin/bash
# 一键安全推送脚本（SSH + Git LFS + 普通 commit）

echo "=== Step 0: 确认远程是 SSH ==="
git remote -v

echo "=== Step 1: 提高 Git buffer 和禁用压缩 ==="
git config --global http.postBuffer 524288000
git config --global core.compression 0

echo "=== Step 2: 确保 LFS track 已开启 ==="
git lfs track "*.zip"
git lfs track "*.pdf"
git lfs track "*.html"
git lfs track "*.db"

# 提交 .gitattributes
git add .gitattributes
git commit -m "chore: update LFS tracking" || echo "No changes to .gitattributes"

echo "=== Step 3: 移除索引中大文件，让 LFS 接管 ==="
git rm --cached *.zip pdf/*.zip *.pdf pdf/*.pdf templates/*.html *.db || echo "No files to remove from index"

echo "=== Step 4: 重新 add 文件，让 LFS 管理大文件 ==="
git add .
git commit -m "chore: move large files to LFS" || echo "No new files to commit"

echo "=== Step 5: Push LFS 对象 ==="
git lfs push origin main

echo "=== Step 6: 分批 push 普通 commit（SSH） ==="
# 先推最近 10 个 commit
git push origin main~10:main || echo "Partial push failed, trying full push"

# 最后推所有 commit
git push origin main

echo "=== Step 7: 完成 ==="
git lfs ls-files
echo "所有大文件已经通过 LFS 上传，普通 commit 已推送"

