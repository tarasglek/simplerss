import listparser as lp
import os, sys
d = lp.parse('greader/subscriptions.xml')
OUTDIR = 'out/feeds/'
for i in d.feeds:
    if os.fork() == 0:
        import feed
        feed.process(i.url, OUTDIR)
        sys.exit(0)

while True:
    try:    
        ret = os.wait()
    except OSError as oe:
        print oe
        break
