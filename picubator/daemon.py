import time
import os
from daemon import Daemon
import sys
import tempfile

def run_daemon():
    if os.environ.get('PICUBATOR_NOOP_DAEMON', 'OFF') == 'ON':
        while True:
            print 'WARNING: no-op daemon enabled!!!'
            time.sleep(5)
    else:
        # Typically want to put imports at top, but that causes issues in non-ARM environments
        from core import main
        main()

class PicubatorDaemon(Daemon):
    def run(self):
        run_daemon()

if __name__ == "__main__":
    temp_dir = tempfile.gettempdir()
    daemon = PicubatorDaemon(os.path.join(temp_dir, '/picubator.pid'))
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
