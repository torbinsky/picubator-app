import time

def noop():
    while True:
        print 'WARNING: no-op daemon enabled!!!'
        time.sleep(5)

if __name__ == '__main__':
    noop()
