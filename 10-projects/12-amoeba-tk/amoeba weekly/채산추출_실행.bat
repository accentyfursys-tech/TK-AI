@echo off
chcp 65001 > nul
echo 채산 데이터 추출 중...
python "%~dp0extract_chaasan.py"
pause