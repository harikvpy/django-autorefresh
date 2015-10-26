from django.contrib.staticfiles.management.commands.runserver import \
        Command as RunServerCommand
from django.utils.autoreload import reloader_thread

import BaseHTTPServer
import thread
import os
import sys
import time

# default port number where we would run the change reporting server
PORT_NUMBER = 32000

# Global state flag that indicates if any of the files in the system
# has changed since last retrieving its value. The state flag will be
# reset from the HTTP request handler that is used to check its state.
_needs_refresh = 0

class SilentHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """
    HTTP Response handler, adapted from sample code in python Wiki.
    Also supresses the connection message which interferes with
    the default Django server messages.

    Probably can be made better, but I'm not going to bother for now.
    """
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/json")
        s.end_headers()

    def do_GET(s):
        global _needs_refresh
        s.send_response(200)
        s.send_header("Content-type", "text/json")
        s.send_header("Access-Control-Allow-Origin", "*")
        s.end_headers()
        s.wfile.write('{ "changed": %d }\n' % _needs_refresh)
        # reset state flag
        _needs_refresh = 0

    def do_POST(s):
        global _needs_refresh
        s.send_response(200)
        s.send_header("Content-type", "text/json")
        s.end_headers()
        _needs_refresh = 1
        s.wfile.write('{ "POST": 1, "changed": %d }\n' % _needs_refresh)

    def log_request(self, *args, **kwargs):
        pass

def refresh_state_server():
    """
    A simple HTTP server that does just one thing, serves a JSON object
    with a single attribute indicating whether the development server
    has been reloaded and therefore browser page requires refreshing.
    """
    httpd = BaseHTTPServer.HTTPServer(("127.0.0.1", PORT_NUMBER), SilentHandler)
    try:
        sys.stdout.write("Starting refresh state server on 127.0.0.1:%d" % PORT_NUMBER)
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
    help = "Starts a lightweight Web server for development and also serves static files."

    def run(self, **options):
        use_reloader = options.get('use_reloader')

        if use_reloader:
            self.autoreload()
        else:
            self.inner_run(None, **options)

    def autoreload(self):
        """
        Copied from django.core.autoload.python_reloader with
        no difference whatsoever.
        """
        if os.environ.get("RUN_MAIN") == "true":
            thread.start_new_thread(self.inner_run, ())
            try:
                print "starting reloader_thread..."
                reloader_thread()
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
        Copied from django.core.autoreload with the difference that
        we set the _needs_refresh state to 1 to indicate that browser
        pages needs to be refreshed.
        """
        global _needs_refresh

        # start the internal HTTP server that will serve the refresh
        # poll requests from our Chrome extenstion
        threadid = thread.start_new_thread(refresh_state_server, ())

        while True:
            args = [sys.executable] + ['-W%s' % o for o in sys.warnoptions] + sys.argv
            if sys.platform == "win32":
                args = ['"%s"' % arg for arg in args]
            new_environ = os.environ.copy()
            new_environ["RUN_MAIN"] = 'true'
            exit_code = os.spawnve(os.P_WAIT, sys.executable, args, new_environ)
            if exit_code != 3:
                return exit_code

            # YES, development server has been restarted.
            # Set the global state flag that will be served to
            # the chrome extension during its next poll

            # a small delay to let the new server completely initialize
            # itself before we set the needs_refresh state flag
            time.sleep(1)
            _needs_refresh = 1

