from django.contrib.staticfiles.management.commands.runserver import \
        Command as RunServerCommand
from django.utils.autoreload import reloader_thread

import BaseHTTPServer
import thread
import os
import sys

# default port number where we would run the change reporting server
REFRESH_PORT = 32000

# Global counter that will be incremented whenever a refresh is required
_needs_refresh = 0
# to hold the last _needs_refresh counter sent to the client
# we compare this against _needs_refresh to determine if the client
# needs to refresh itself
_last_refresh = 0

_refresh_port = REFRESH_PORT

class SilentHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """
    HTTP Response handler, adapted from sample code in python Wiki.
    Supresses the connection message which interferes with
    the default Django server messages.

    Probably can be made better, but I'm not going to bother for now.
    """
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/json")
        s.end_headers()

    def do_GET(s):
        # GET returns a boolean indicating if browser page needs
        # to be refreshed
        global _needs_refresh
        global _last_refresh
        s.send_response(200)
        s.send_header("Content-type", "text/json")
        s.end_headers()
        s.wfile.write('{ "changed": %d }\n' % s.needs_refresh())
        _last_refresh = _needs_refresh

    def do_POST(s):
        '''POST can be used to force a refresh externally'''
        global _needs_refresh
        s.send_response(200)
        s.send_header("Content-type", "text/json")
        s.end_headers()
        _needs_refresh += 1
        s.wfile.write('{ "POST": 1, "changed": %d }\n' % s.needs_refresh())

    def needs_refresh(self):
        '''returns a boolean indicating if a refresh is required'''
        global _needs_refresh
        global _last_refresh
        return _needs_refresh != _last_refresh

    def log_request(self, *args, **kwargs):
        pass

def refresh_state_server():
    """
    A simple HTTP server that does just one thing, serves a JSON object
    with a single attribute indicating whether the development server
    has been reloaded and therefore browser page requires refreshing.

    Extended to accept a POST request which forces the refresh flag
    """
    httpd = BaseHTTPServer.HTTPServer(("127.0.0.1", _refresh_port),
            SilentHandler)
    try:
        sys.stdout.write("Starting auto refresh state server at 127.0.0.1:%d\n" \
                % _refresh_port)
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

class Command(RunServerCommand):
    """
    A customized version of the runserver command that spawns a secondary
    http server which can be queried to check if the Django development
    server has been reloaded (and therefore the browser page needs refresh)
    """
    help = "Starts a lightweight Web server for development that serves static files and provides refresh status through a secondary HTTP server running at %d." % _refresh_port

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('--refreshport', action='store', default=32000, type=int,
            help='Port number where the refresh server listens. Defaults to 32000')

    def run(self, **options):
        use_reloader = options.get('use_reloader')
        global _refresh_port
        _refresh_port = options.get('refreshport', REFRESH_PORT)

        if use_reloader:
            self.autoreload()
        else:
            self.inner_run(None, **options)

    def autoreload(self):
        """Copied from django.core.autoload.python_reloader"""
        if os.environ.get("RUN_MAIN") == "true":
            thread.start_new_thread(self.inner_run, ()) # start http server
            try:
                #sys.stdout.write("Starting reloader_thread...\n")
                reloader_thread()   # poll source files for modifications
                                    # if modified, kill self
            except KeyboardInterrupt:
                pass
        else:
            try:
                exit_code = self.restart_with_reloader()
                if exit_code < 0:
                    os.kill(os.getpid(), -exit_code)
                else:
                    sys.exit(exit_code)
            except KeyboardInterrupt:
                pass

    def restart_with_reloader(self):
        """
        Differs from django.core.autoreload in that _needs_refresh counter
        is incremented everytime the Development server is reloaded owing
        to detected file changes.
        """
        global _needs_refresh
        global _last_refresh

        # start the internal HTTP server that will serve the refresh
        # poll requests from our Chrome extenstion
        threadid = thread.start_new_thread(refresh_state_server, ())

        while True:
            args = [sys.executable] + ['-u'] + ['-W%s' % o for o in sys.warnoptions] + sys.argv
            if sys.platform == "win32":
                args = ['"%s"' % arg for arg in args]
            new_environ = os.environ.copy()
            new_environ["RUN_MAIN"] = 'true'
            import subprocess
            proc = subprocess.Popen(args,
                    bufsize=1,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    env=new_environ,
                    close_fds=True)

            # We loop reading all the output of the child process
            # until it prints the 'Quit the server with CONTROL'
            # When that's done, we can be certain that the server
            # is fully initialized and ready to serve pages
            while True and proc.returncode == None:
                line = proc.stdout.readline()
                if line:
                    print line,
                    if 'Quit the server with CONTROL' in line:
                        break;
                proc.poll()

            # Since the development server is fully initialized,
            # we can now set the refresh state flag
            sys.stdout.write("Development server reinitialized, setting refresh flag\n")
            _needs_refresh += 1

            # Read any messages printed by the development server to stdout
            # and reprint them.
            while True and proc.returncode == None:
                line = proc.stdout.readline()
                if line:
                    print line,
                proc.poll()

            sys.stdout.write("Development server terminated with exit code %d\n" % proc.returncode)
            if proc.returncode != 3:
                return proc.returncode

