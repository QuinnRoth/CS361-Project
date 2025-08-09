import subprocess
import time

VENVPATH = r"C:\Users\qtrot\PycharmProjects\battleshipTest\.venv\Scripts\python.exe"

processes = []

processes.append(subprocess.Popen([VENVPATH, "main.py"]))

time.sleep(1)

processes.append(subprocess.Popen([VENVPATH, "game_logic.py"]))

time.sleep(1)

processes.append(subprocess.Popen([VENVPATH, "render_board.py"]))

time.sleep(1)

processes.append(subprocess.Popen([VENVPATH, "opponent.py"]))

for process in processes:
    process.wait()
