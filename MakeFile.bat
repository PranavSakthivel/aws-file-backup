@echo on
set p=%cd%
pip install pyinstaller
pip install boto3
pyinstaller.exe -F --debug all backup.py
pyinstaller.exe -F --debug all restore.py
move "%cd%\dist\backup.exe" backup.exe
move "%cd%\dist\restore.exe" restore.exe
start cmd /k echo Examples: python backup.py "C:\Users\Pranav\Desktop\Test", python restore.py "C:\Users\Pranav\Desktop\Restore" "backupbucket123", Please read the documentation for further information.
Pause