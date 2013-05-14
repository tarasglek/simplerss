import os
import os.path
import sys
import json
import feedparser
import time
import re
import operator

def get_href(links):
    for l in links:
        if l['type'] == 'text/html':
            return l['href']

def get_img(links):
    for l in links:
        if l['type'][:6] == 'image/':
            return "<img src='%s'>" % l['href']
        else:
            print l['type']
    return ""

def mergeReverseSortedLists(a, b):
    l = []
    while a and b:
        if a[0]['updated'] > b[0]['updated']:
            l.append(a.pop(0))
        else:
            l.append(b.pop(0))
    return l + a + b

INDIR = sys.argv[1]
OUTDIR = sys.argv[2]
feedmetas = []
all_entries = []
for f in os.listdir(INDIR):
    path = os.path.join(INDIR, f)
    with open(path) as i:
        feed = json.loads(i.read())
        feedindex = len(feedmetas)
        feedmetas.append(feed['feed'])
        feed['feed']['filename'] = f
        for e in feed['entries']:
            try:
                e['updated'] = feedparser._parse_date(e['updated'])
            except KeyError:
                print 'Falling back on feed.modified for %s' % path
                try:
                    e['updated'] = feedparser._parse_date(feed['feed']['updated'])
                except KeyError:
                    try:
                        print 'Falling back on http.modified for %s' % path
                        e['updated'] = time.gmtime(feed['modified'])
                    except KeyError:
                        print 'Falling back on stat(%s)' % path                    
                        mtime = os.stat(path).st_mtime
                        feed['modified'] = mtime
                        e['updated'] = time.gmtime(mtime)
            e['feedindex'] = feedindex
        all_entries = mergeReverseSortedLists(all_entries, feed['entries'])

invalid_url_regex = re.compile('[<>\n]')

feedkey={}

with open(os.path.join(OUTDIR, "index.html"),'w') as outf:
    outf.write("""<html>
<head>
<meta name="viewport" content="width=320; initial-scale=1; maximum-scale=1" />
<link href="feed.css" rel="stylesheet" type="text/css" />
</head>
<body><ul id='feeds'>""")
    for i in range(0, min(len(all_entries), 100)):
        e = all_entries[i]
        feedindex = e['feedindex']
        try:
            feedkey[feedindex]+=1
        except KeyError:
            feedkey[feedindex] = 1
        filename = feedmetas[feedindex]['filename']
        try:
            href = get_href(e['links'])
        except KeyError:
            href = e['href']

        if invalid_url_regex.search(href):
            print "%s has weird url: %s" % (filename, href)
            continue
        try:
            outf.write("<!--%s --><li class='feed%d'><a href='%s' target='_blank'>%s</a><desc>%s</desc></li>\n" % 
                       (filename, feedindex, href, e['title'], feedmetas[feedindex]['title']))
        except UnicodeEncodeError:
            print "unicode error while printing %s" % filename
    outf.write("</ul><ul id='navlist'>")
    outf.write("<li><button id=display_all data-feed='*' style='display:none'>All</button></li>")
    for feedindex, count in sorted(feedkey.iteritems(), key=operator.itemgetter(1), reverse=True):
        feed = feedmetas[feedindex]
        img = ''
        try:
            img = "<img src='%s'>"%feed['icon']
        except KeyError:
            pass
        try:
            print feed['title']
            outf.write("<li><button data-feed='%d' data-json='%s'>%s %s(%d)</button></li>" % (feedindex, feed['filename'], img, feed['title'],count))
        except UnicodeEncodeError:
            pass
    outf.write("""</ul><script src='jquery.js'></script>
<script type="application/javascript;version=1.8" src='tarss.js'>
</script>
</body></html>""")
    print len(all_entries)
