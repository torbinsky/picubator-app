import daemon

from main import do_main_program

with daemon.DaemonContext():
    do_main_program()
