# Copyright (c) 2015 Jesse Weaver.
#
# This file is part of supybot-remote.
# 
# supybot-remote is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# supybot-remote is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with supybot-remote. If not, see <http://www.gnu.org/licenses/>.

# Portions adapted from
# https://github.com/ProgVal/Supybot-plugins/blob/3d0a6a948de996c91a2b2b89afcc965ee99d6f50/WebStats/plugin.py,
# which has the following license:
###
# Copyright (c) 2010-2011, Valentin Lorentz
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
###

import supybot.callbacks as callbacks
from supybot.commands import *
import supybot.conf as conf
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.log as log
import supybot.utils as utils
import supybot.world as world

import BaseHTTPServer
import cgi
import threading
import time

class HTTPHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        log.info(
            "HTTP: %s - - [%s] %s" % (
                self.client_address[0],
                self.log_date_time_string(),
                format % args
            )
        )

    def do_POST(self):
        output = ''
        splittedPath = self.path.split('/')

        response = 404
        content_type = 'text/html'
        output = '404 Not Found\n'

        try:
            ctype = self.headers.getheader('content-type')
            if ctype == 'application/x-www-form-urlencoded':
                length = int(self.headers.getheader('content-length'))
                postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
            else:
                postvars = {}

            if postvars.get('apiKey', [''])[0] == self.server.plugin.registryValue('apiKey'):
                if 'destination' in postvars and 'message' in postvars:
                    response = 200
                    content_type = 'application/json'
                    self.server.plugin._announce(postvars['destination'][0], postvars['message'][0])
                    output = '{"success":true}\n'
                else: 
                    response = 403
                    content_type = 'application/json'
                    output = '{"success":false,"error":"Missing parameters"}\n'
            else:
                response = 403
                content_type = 'application/json'
                output = '{"success":false,"error":"Invalid API key"}\n'
        finally:
            self.send_response(response)
            self.send_header('Content-Type', content_type)
            self.end_headers()
            self.wfile.write(output)

class HTTPServer(BaseHTTPServer.HTTPServer):
    """A simple class that set a smaller timeout to the socket"""
    timeout = 0.3

class ServerThread:
    def __init__(self, plugin):
        self.serve = True
        self._plugin = plugin

    def run(self):
        serverAddress = (self._plugin.registryValue('host'), self._plugin.registryValue('port'))
        while True:
            time.sleep(1)
            try:
                httpd = HTTPServer(serverAddress, HTTPHandler)
                break
            except:
                continue

        log.info('HTTPRemote web server launched')
        httpd.plugin = self._plugin
        while self.serve:
            httpd.handle_request()
        log.info('HTTPRemote web server stopped')
        httpd.server_close()
        time.sleep(1) # Let the socket be really closed

class HTTPRemote(callbacks.Plugin):
    """HTTP server designed to receive announcements and commands from the outside world."""
    def __init__(self, irc):
        super(HTTPRemote, self).__init__(irc)
        self._server = ServerThread(self)
        threading.Thread(
            target = self._server.run,
            name = "HTTPRemote server"
        ).start()
    
    def _announce(self, destination, message):
        irc = world.ircs[0]
        irc.queueMsg(ircmsgs.privmsg(destination, self.registryValue('messagePrefix') + message))

    def die(self):
        self._server.serve = False

Class = HTTPRemote

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
