import sys

import sdnotify

def ready():
    # Inform systemd that we've finished our startup sequence...
    n = sdnotify.SystemdNotifier()
    n.notify("READY=1")

if __name__ == '__main__':
    if(len(sys.argv) == 1):
        # Note: normally I put all imports at top, but this stuff won't work in a non-ARM environment
        # For integration testing purposes, we allow a 'noop' mode which doesn't import stuff that breaks
        # in non-ARM environments
        from core import init, main
        # Initialize service
        unit = init()

        # We are ready
        ready()

        # Begin main loop
        main(unit)
    elif('noop' in sys.argv):
        ready()
    else:
        sys.exit(1)
