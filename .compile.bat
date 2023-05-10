set compile_command=import os,compileall;compileall.compile_dir(os.getcwd(),force=True,quiet=True)

"%ProgramFiles%/Autodesk/Maya2020/bin/mayapy" -c "%compile_command%"
"%ProgramFiles%/Autodesk/Maya2022/bin/mayapy" -c "%compile_command%"