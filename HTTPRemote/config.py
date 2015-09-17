# Copyright (c) 2015 Jesse Weaver.
#
# This file is part of supybot-httpremote.
# 
# supybot-httpremote is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# supybot-httpremote is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with supybot-httpremote. If not, see <http://www.gnu.org/licenses/>.

import random
import string
import supybot.conf as conf
import supybot.registry as registry

def configure(advanced):
    # This will be called by setup.py to configure this module.  Advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('HTTPRemote', True)

default_key = ''.join(random.choice('0123456789abcdef') for x in range(64))

HTTPRemote = conf.registerPlugin('HTTPRemote')
conf.registerGlobalValue(HTTPRemote, 'apiKey',
    registry.String(default_key, """The API key used by external services to send commands.""", private = True))
conf.registerGlobalValue(HTTPRemote, 'host',
    registry.String("0.0.0.0", """The host for the HTTP server to listen on."""))
conf.registerGlobalValue(HTTPRemote, 'port',
    registry.PositiveInteger(7247, """The port for the HTTP server to listen on."""))
conf.registerGlobalValue(HTTPRemote, 'messagePrefix',
    registry.String('(remote) ', """String to prefix to all remote messages."""))

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
