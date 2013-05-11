import listparser as lp
import feed

d = lp.parse('greader/subscriptions.xml')
OUTDIR = 'out/'
for i in d.feeds:
    feed.process(i.url, OUTDIR)
