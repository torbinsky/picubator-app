import sdnotify

from core import init, main

if __name__ == '__main__':
    # Initialize service
    init()

    # Inform systemd that we've finished our startup sequence...
    n = sdnotify.SystemdNotifier()
    n.notify("READY=1")

    # Begin main loop
    main()
