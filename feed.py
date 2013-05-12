import feedparser
import sys
import re
import json
import time
import os.path
import hashlib

def url2file(url, out):
    name = re.sub(r'[^A-z.-]','_', url)
    if len(name) > 200:
        name = hashlib.md5(url).hexdigest()
    return os.path.join(out, name + ".json")

def process_additions(entries, old):
    def entry_uid(e):
        try:
            return e['links']
        except KeyError:
            pass
        return (e['title'], e['content'])
    
    if old == None:
        return entries
    out = []
    # dedup based on link to article
    for e in entries:
        e_uid = entry_uid(e)
        for o in old:
            if e_uid == entry_uid(o) and (not ('updated' in e and 'updated' in o) or e['updated'] == o['updated']):
                e = None
                #print "Duplicate %s" % str(e_uid)
                break
        if e == None:
            continue
        out.append(e)
    for o in old:
        out.append(o)
    # limit to 30 old entries
    return out[:30]

def sanitize_for_json(d):
    del_keys = []
    for k, v in d.iteritems():
        if type(v) in [feedparser.FeedParserDict, time.struct_time]:
            del_keys.append(k)
    for k in del_keys:
        del d[k]
    """
    for k,v in d.iteritems():
        print k,type(v)
        """
    return d

def process(url, outdir):
    fname = url2file(url, outdir)
    print "%s -> %s" % (url, fname)
    old = None
    old_modified = None
    try:
        old = json.loads(open(fname).read())
        if 'modified' in old:
            old_modified = time.gmtime(old['modified'])
    except IOError:
        pass
    except ValueError:
        print "invalid json"
        pass
    d = feedparser.parse(url, modified=old_modified)
    feed = sanitize_for_json(d['feed'])
    if len(feed) == 0:
        print "Empty feed %s" % url
        return
    entries = []
    for e in d['entries']:
        entries.append(sanitize_for_json(e))

    if old != None:
        entries = process_additions(entries, old['entries'])
        if entries == old['entries']:
            print "No new entries added, %s not modified" % fname
            return

    out = {}
    if old != None:
        out = old
    
    out['feed'] = feed
    out['entries'] = entries
    out['url'] = url
    try:
        out['etag'] = d.etag
    except AttributeError:
        pass

    try:
        out['icon'] = d.icon
    except AttributeError:
        pass

    try:
        out['modified'] = time.mktime(d.modified)
    except AttributeError:
        pass

    outstr = json.dumps(out)
    outf = open(fname,'w')
    outf.write(outstr)
    outf.close()

if __name__ == "__main__": 
    process(sys.argv[1], "out/")
