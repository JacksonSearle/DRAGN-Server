import unreal
import subprocess
import pkg_resources
from pathlib import Path

#content_path = unreal.Paths.project_content_dir() + "Python/"

PYTHON_INTERPRETER_PATH = unreal.get_interpreter_executable_path()
assert Path(PYTHON_INTERPRETER_PATH).exists(), f"Python not found at '{PYTHON_INTERPRETER_PATH}'"

def pip_install(packages):
    # dont show window
    info = subprocess.STARTUPINFO()
    info.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    print("installing")
    proc = subprocess.Popen(
        [
            PYTHON_INTERPRETER_PATH, 
            '-m', 'pip', 'install', 
            '--no-warn-script-location', 
            *packages
        ],
        startupinfo = info,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        encoding = "utf-8"
    )

    while proc.poll() is None:
        unreal.log(proc.stdout.readline().strip())
    #    unreal.log_warning(proc.stderr.readline().strip())

    return proc.poll()

# Put here your required python packages
required = {'tqdm', 'sentence-transformers', 'openai', 'python-dotenv'}
installed = {pkg.key for pkg in pkg_resources.working_set}
# print("All packages", installed)
missing = required - installed
# print("all missing", missing)

if len(missing) > 0:
    # print("here we r")
    pip_install(missing)
else:
    unreal.log("All python requirements already satisfied")

print("python worked")

import main
@unreal.uclass()
class RunPythonCodeImplementation(unreal.RunPythonCode) :
    
    @unreal.ufunction(override = True)
    def TestFunc(self):
        unreal.log_warning("Wow! This is the BEST")

    @unreal.ufunction(override=True)
    def StartBackEnd(self):
        main.main()
        print("succesfully ran")
    
    # @unreal.ufunction(override=True)
    # def StopBackEnd(self):
    #     print("didn't kill the thread")