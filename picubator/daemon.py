import daemon
import time

class PicubatorDaemon(Daemon):
    def run(self):
        if os.environ.get('PICUBATOR_KITCHEN_VERIFY', 'OFF') == 'ON':
            while True:
                print 'WARNING: Kitchen verify mode enabled!'
                time.sleep(5)
        else:
            # Typically want to put imports at top, but that causes issues in non-ARM environments
            from core import main
            main()

if __name__ == "__main__":
    daemon = PicubatorDaemon('/tmp/picubator.pid')
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
