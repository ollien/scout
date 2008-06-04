import scout
import sys
import httplib
import urllib
from xml.dom import minidom

class ScoutModule(object):

    name = "webpin"
    desc = "Search in the packages using the webpin webservice."
    distros = {
        '10.3'    : 'openSUSE_103',
        '10.2'    : 'openSUSE_102',
        '10.1'    : 'SUSE_Linux_101',
        'Factory' : 'SUSE_Factory',
        'default' : 'SUSE_Factory'
    }
    service_host = 'api.opensuse-community.org'
    service_baseurl = '/searchservice/Search/Simple/'


    @classmethod
    def query(cls, term):
        try:
            url = cls.service_baseurl + cls.distros['default'] + '/' + urllib.quote(term)
            c = httplib.HTTPConnection(cls.service_host)
            c.connect()
            c.putrequest('GET', 'http://%s%s' % (cls.service_host, url))
            c.putheader('User-Agent', 'scout')
            c.putheader('Accept', 'text/xml')
            c.endheaders()
            r = c.getresponse()
            data = r.read()
            r.close()
            return minidom.parseString(data)
        except Exception, e:
            print 'Cannot retreive query results ... %s' % e
            return None

    @classmethod
    def main(cls):
        if len(sys.argv) < 2:
            print 'Enter the term to look for ...'
            return None

        term = sys.argv[1]

        dom = cls.query(term)
        root = dom.getElementsByTagNameNS('http://datastructures.pkgsearch.benjiweber.co.uk', 'packages').item(0)

        result = scout.Result( ['pkg', 'ver', 'arch', 'repo', 'files'], ['package', 'version', 'arch', 'repository URL', 'matched files']);

        for node in root.getElementsByTagName("package"):
            name = node.getElementsByTagName('name').item(0).childNodes.item(0).nodeValue
            version = node.getElementsByTagName('version').item(0).childNodes.item(0).nodeValue
            summary = node.getElementsByTagName('summary').item(0).childNodes.item(0).nodeValue
            repoURL = node.getElementsByTagName('repoURL').item(0).childNodes.item(0).nodeValue
            archs = []
            archsNode = node.getElementsByTagName('archs').item(0)
            if archsNode:
                for archNode in archsNode.getElementsByTagName('arch'):
                    archs.append(archNode.childNodes.item(0).nodeValue)
            archs = ' '.join(archs)
            fileMatches = []
            for matchedFileNameNode in node.getElementsByTagName('matchedFileName'):
                fileMatches.append(matchedFileNameNode.childNodes.item(0).nodeValue.strip())
            fileMatches = ' '.join(fileMatches)

            result.addrow([name, version, archs, repoURL, fileMatches]);

        return result
