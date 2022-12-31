from Monitoring.components import *
import logging
import cherrypy
import time
import threading
import sys
import json
import os





if not hasattr(logging, 'statistics'):
    logging.statistics = {}

def extrapolate_statistics(scope):
    """Return an extrapolated copy of the given scope."""
    c = {}
    for k, v in scope.copy().items():

        if isinstance(v, dict):
            v = extrapolate_statistics(v)
        elif isinstance(v, (list, tuple)):
            v = [extrapolate_statistics(record) for record in v]
        elif hasattr(v, '__call__'):
            v = v(scope)
        if type(k) is not int and 'Cheroot HTTPServer' in k:  # skipping the cheroot server metrics
            pass
        else:

            c[k] = v
    return c


# -------------------- CherryPy Applications Statistics --------------------- #

appstats = logging.statistics.setdefault('CherryPy Applications', {})
appstats.update({
    'Enabled': True,
    'Bytes Read/Request': lambda s: (
        s['Total Requests'] and
        (s['Total Bytes Read'] / float(s['Total Requests'])) or
        0.0
    ),
    'Bytes Read/Second': lambda s: s['Total Bytes Read'] / s['Uptime'](s),
    'Bytes Written/Request': lambda s: (
        s['Total Requests'] and
        (s['Total Bytes Written'] / float(s['Total Requests'])) or
        0.0
    ),
    'Bytes Written/Second': lambda s: (
        s['Total Bytes Written'] / s['Uptime'](s)
    ),
    'Current Time': lambda s: time.time(),
    'Current Requests': 0,
    'Requests/Second': lambda s: float(s['Total Requests']) / s['Uptime'](s),
    'Server Version': cherrypy.__version__,
    'Start Time': time.time(),
    'Total Bytes Read': 0,
    'Total Bytes Written': 0,
    'Total Requests': 0,
    'Total Time': 0,
    'Uptime': lambda s: time.time() - s['Start Time'],
    'Gc Count': get_gcobjects(),
    'Memory' : get_memoryinmb(),
    'Cpu Percent' : get_cpupercentage(),
    'Requests': {},
})


def proc_time(s):
    return time.time() - s['Start Time']


class ByteCountWrapper(object):

    """Wraps a file-like object, counting the number of bytes read."""

    def __init__(self, rfile):
        self.rfile = rfile
        self.bytes_read = 0

    def read(self, size=-1):
        data = self.rfile.read(size)
        self.bytes_read += len(data)
        return data

    def readline(self, size=-1):
        data = self.rfile.readline(size)
        self.bytes_read += len(data)
        return data

    def readlines(self, sizehint=0):
        # Shamelessly stolen from StringIO
        total = 0
        lines = []
        line = self.readline()
        while line:
            lines.append(line)
            total += len(line)
            if 0 < sizehint <= total:
                break
            line = self.readline()
        return lines

    def close(self):
        self.rfile.close()

    def __iter__(self):
        return self

    def next(self):
        data = self.rfile.next()
        self.bytes_read += len(data)
        return data


def average_uriset_time(s):
    return s['Count'] and (s['Sum'] / s['Count']) or 0


def _get_threading_ident():
    if sys.version_info >= (3, 3):
        return threading.get_ident()
    return threading._get_ident()


class StatsTool(cherrypy.Tool):

    """Record various information about the current request."""

    def __init__(self):

        cherrypy.Tool.__init__(self, 'on_end_request', self.record_stop)

    def _setup(self):
        """Hook this tool into cherrypy.request.
        The standard CherryPy request object will automatically call this
        method when the tool is "turned on" in config.
        """

        if appstats.get('Enabled', False):
            cherrypy.Tool._setup(self)
            self.record_start()

    def record_start(self):
        """Record the beginning of a request."""
        request = cherrypy.serving.request
        if not hasattr(request.rfile, 'bytes_read'):
            request.rfile = ByteCountWrapper(request.rfile)
            request.body.fp = request.rfile

        r = request.remote

        appstats['Current Requests'] += 1
        appstats['Total Requests'] += 1
        appstats['Gc Count'] = get_gcobjects()
        appstats['Memory'] = get_memoryinmb()
        appstats['Cpu Percent'] = get_cpupercentage()
        appstats['Requests'][_get_threading_ident()] = {
            'Bytes Read': None,
            'Bytes Written': None,
            # Use a lambda so the ip gets updated by tools.proxy later
            'Client': lambda s: '%s:%s' % (r.ip, r.port),
            'Start Time': time.time(),
            'End Time': None,
            'Processing Time': proc_time,
            'Request-Line': request.request_line,
            'Response Status': None,

        }

    def record_stop(
            self, uriset=None, queries_count=1000,
            debug=False, **kwargs):
        """Record the end of a request."""
        resp = cherrypy.serving.response
        w = appstats['Requests'][_get_threading_ident()]

        r = cherrypy.request.rfile.bytes_read
        w['Bytes Read'] = r
        appstats['Total Bytes Read'] += r

        if resp.stream:
            w['Bytes Written'] = 'chunked'
        else:
            cl = int(resp.headers.get('Content-Length', 0))
            w['Bytes Written'] = cl
            appstats['Total Bytes Written'] += cl

        w['Response Status'] = \
            getattr(resp, 'output_status', resp.status).decode()

        w['End Time'] = time.time()
        p = w['End Time'] - w['Start Time']
        w['Processing Time'] = p
        appstats['Total Time'] += p

        appstats['Current Requests'] -= 1
        appstats['Gc Count'] = get_gcobjects()
        appstats['Memory'] = get_memoryinmb()
        appstats['Cpu Percent'] = get_cpupercentage()

        w['Memory'] = appstats['Memory']
        w['request Proc'] = appstats['Current Requests']

        if debug:
            cherrypy.log('Stats recorded: %s' % repr(w), 'TOOLS.CPSTATS')

        if uriset:
            rs = appstats.setdefault('URI Set Tracking', {})
            r = rs.setdefault(uriset, {
                'Min': None, 'Max': None, 'Count': 0, 'Sum': 0,
                'Avg': average_uriset_time})
            if r['Min'] is None or p < r['Min']:
                r['Min'] = p
            if r['Max'] is None or p > r['Max']:
                r['Max'] = p
            r['Sum'] += p


        sq = appstats.setdefault('Urls', [])
        sq.append(w.copy())
        if len(sq) > queries_count:
            sq.pop(0)


cherrypy.tools.cpstats = StatsTool()


# ---------------------- CherryPy Statistics Reporting ---------------------- #

thisdir = os.path.abspath(os.path.dirname(__file__))

missing = object()


def locale_date(v):
    return time.strftime('%c', time.gmtime(v))


def iso_format(v):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(v))


def pause_resume(ns):
    def _pause_resume(enabled):
        pause_disabled = ''
        resume_disabled = ''
        if enabled:
            resume_disabled = 'disabled="disabled" '
        else:
            pause_disabled = 'disabled="disabled" '
        return """
            <form action="pause" method="POST" style="display:inline">
            <input type="hidden" name="namespace" value="%s" />
            <input type="submit" value="Pause" %s/>
            </form>
            <form action="resume" method="POST" style="display:inline">
            <input type="hidden" name="namespace" value="%s" />
            <input type="submit" value="Resume" %s/>
            </form>
            """ % (ns, pause_disabled, ns, resume_disabled)
    return _pause_resume


class StatsPage(object):

    formatting = {
        'CherryPy Applications': {
            'Enabled': pause_resume('CherryPy Applications'),
            'Bytes Read/Request': '%.3f',
            'Bytes Read/Second': '%.3f',
            'Bytes Written/Request': '%.3f',
            'Bytes Written/Second': '%.3f',
            'Current Time': iso_format,
            'Requests/Second': '%.3f',
            'Start Time': iso_format,
            'Total Time': '%.3f',
            'Uptime': '%.3f',
            'Queries': {
                'End Time': None,
                'Processing Time': '%.3f',
                'Start Time': iso_format,
            },
            'URI Set Tracking': {
                'Avg': '%.3f',
                'Max': '%.3f',
                'Min': '%.3f',
                'Sum': '%.3f',
            },
            'Requests': {
                'Bytes Read': '%s',
                'Bytes Written': '%s',
                'End Time': None,
                'Processing Time': '%.3f',
                'Start Time': None,
            },
        },
        'CherryPy WSGIServer': {
            'Enabled': pause_resume('CherryPy WSGIServer'),
            'Connections/second': '%.3f',
            'Start time': iso_format,
        },
    }

    @cherrypy.expose
    def index(self):
        # Transform the raw data into pretty output for HTML
        yield """
<html>
<head>
    <title>Statistics</title>
<style>
th, td {
    padding: 0.25em 0.5em;
    border: 1px solid #666699;
}
table {
    border-collapse: collapse;
}
table.stats1 {
    width: 100%;
}
table.stats1 th {
    font-weight: bold;
    text-align: right;
    background-color: #CCD5DD;
}
table.stats2, h2 {
    margin-left: 50px;
}
table.stats2 th {
    font-weight: bold;
    text-align: center;
    background-color: #CCD5DD;
}
</style>
</head>
<body>
"""
        for title, scalars, collections in self.get_namespaces():
            yield """
<h1>%s</h1>
<table class='stats1'>
    <tbody>
""" % title
            for i, (key, value) in enumerate(scalars):
                colnum = i % 3
                if colnum == 0:
                    yield """
        <tr>"""
                yield (
                    """
            <th>%(key)s</th><td id='%(title)s-%(key)s'>%(value)s</td>""" %
                    vars()
                )
                if colnum == 2:
                    yield """
        </tr>"""

            if colnum == 0:
                yield """
            <th></th><td></td>
            <th></th><td></td>
        </tr>"""
            elif colnum == 1:
                yield """
            <th></th><td></td>
        </tr>"""
            yield """
    </tbody>
</table>"""

            for subtitle, headers, subrows in collections:
                yield """
<h2>%s</h2>
<table class='stats2'>
    <thead>
        <tr>""" % subtitle
                for key in headers:
                    yield """
            <th>%s</th>""" % key
                yield """
        </tr>
    </thead>
    <tbody>"""
                for subrow in subrows:
                    yield """
        <tr>"""
                    for value in subrow:
                        yield """
            <td>%s</td>""" % value
                    yield """
        </tr>"""
                yield """
    </tbody>
</table>"""
        yield """
</body>
</html>
"""

    def get_namespaces(self):
        """Yield (title, scalars, collections) for each namespace."""
        # for key in logging.statistics.keys():
        #     if 'Cheroot HTTPServer' in key:
        #         logging.statistics[key]['Enabled'] = True

        s = extrapolate_statistics(logging.statistics)
        # print(s)
        for title, ns in sorted(s.items()):
            scalars = []
            collections = []
            ns_fmt = self.formatting.get(title, {})
            for k, v in sorted(ns.items()):
                fmt = ns_fmt.get(k, {})
                if isinstance(v, dict):
                    headers, subrows = self.get_dict_collection(v, fmt)
                    collections.append((k, ['ID'] + headers, subrows))
                elif isinstance(v, (list, tuple)):
                    headers, subrows = self.get_list_collection(v, fmt)
                    collections.append((k, headers, subrows))
                else:
                    format = ns_fmt.get(k, missing)
                    if format is None:
                        # Don't output this column.
                        continue
                    if hasattr(format, '__call__'):
                        v = format(v)
                    elif format is not missing:
                        v = format % v
                    scalars.append((k, v))
            yield title, scalars, collections

    def get_dict_collection(self, v, formatting):
        """Return ([headers], [rows]) for the given collection."""
        # E.g., the 'Requests' dict.
        headers = []
        vals = v.values()
        for record in vals:
            for k3 in record:
                format = formatting.get(k3, missing)
                if format is None:
                    # Don't output this column.
                    continue
                if k3 not in headers:
                    headers.append(k3)
        headers.sort()

        subrows = []
        for k2, record in sorted(v.items()):
            subrow = [k2]
            for k3 in headers:
                v3 = record.get(k3, '')
                format = formatting.get(k3, missing)
                if format is None:
                    # Don't output this column.
                    continue
                if hasattr(format, '__call__'):
                    v3 = format(v3)
                elif format is not missing:
                    v3 = format % v3
                subrow.append(v3)
            subrows.append(subrow)

        return headers, subrows

    def get_list_collection(self, v, formatting):
        """Return ([headers], [subrows]) for the given collection."""
        # E.g., the 'Slow Queries' list.
        headers = []
        for record in v:
            for k3 in record:
                format = formatting.get(k3, missing)
                if format is None:
                    # Don't output this column.
                    continue
                if k3 not in headers:
                    headers.append(k3)
        # headers.sort()

        subrows = []
        for record in v:
            subrow = []
            for k3 in headers:
                v3 = record.get(k3, '')
                format = formatting.get(k3, missing)
                if format is None:
                    # Don't output this column.
                    continue
                if hasattr(format, '__call__'):
                    v3 = format(v3)
                elif format is not missing:
                    v3 = format % v3
                subrow.append(v3)
            subrows.append(subrow)

        return headers, subrows

    if json is not None:
        @cherrypy.expose
        def data(self):
            print()
            s = extrapolate_statistics(logging.statistics)
            cherrypy.response.headers['Content-Type'] = 'application/json'
            return json.dumps(s, sort_keys=True, indent=4).encode('utf-8')

    @cherrypy.expose
    def pause(self, namespace):
        logging.statistics.get(namespace, {})['Enabled'] = False
        raise cherrypy.HTTPRedirect('./')
    pause.cp_config = {'tools.allow.on': True,
                       'tools.allow.methods': ['POST']}

    @cherrypy.expose
    def resume(self, namespace):
        logging.statistics.get(namespace, {})['Enabled'] = True
        raise cherrypy.HTTPRedirect('./')
    resume.cp_config = {'tools.allow.on': True,
                        'tools.allow.methods': ['POST']}

