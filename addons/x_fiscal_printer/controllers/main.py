# -*- coding: utf-8 -*-
##############################################################################
#
#    fiscal_printer
#    Copyright (C) 2014 No author.
#    No email
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import base64
import openerp.addons.web.http as oeweb
from openerp.addons.web.controllers.main import content_disposition
import psycopg2
import sys
import json
from multiprocessing import Process

from Queue import Queue

access_control_allow_origin = 'chrome-extension://dpcgdmgjbideciclegnjoafkpblgnlgd/'
event_hub = {}
result_hub = {}

## Monkey path for HttpRequest
http_old_dispatch = oeweb.HttpRequest.dispatch

def http_dispatch(self, method):
    r = http_old_dispatch(self, method)
    if hasattr(r, 'headers'):
        r.headers._list.append(('Access-Control-Allow-Origin',access_control_allow_origin))
        r.headers._list.append(('Access-Control-Allow-Credentials', 'true'))
    return r

oeweb.HttpRequest.dispatch = http_dispatch

## Monkey path for JsonRequest
json_old_dispatch = oeweb.JsonRequest.dispatch

def json_dispatch(self, method):
    r = json_old_dispatch(self, method)
    if hasattr(r, 'headers'):
        r.headers._list.append(('Access-Control-Allow-Origin',access_control_allow_origin))
        r.headers._list.append(('Access-Control-Allow-Credentials', 'true'))
    return r

oeweb.JsonRequest.dispatch = json_dispatch

## Event manager
def do_event(event, data={}, session_ids=None):
    event_result = {}
    item = {
        'event': event,
        'data': json.dumps(data),
    }

    session_ids = session_ids if session_ids else event_hub.keys()

    print "DO EVENT", event, data, session_ids

    for k in session_ids:
        try:
            print "do_event: PUT", k
            event_hub[k].put(item, True, 10)
            r = result_hub[k].get()
            print "do_event: GET"
            result_hub[k].task_done()
            print "do_event: TASK DONE"
            event_result[k] = r
        except Queue.Full:
            _logger.warning("Queue put timeout for session %s:" % k)
            pass
        except:
            _logger.error("Unexpected error for session %s:" % k, sys.exc_info()[0])
            raise

    return dict( (k, event_result[k]) for k in session_ids if k in event_result )

def do_return(req, result):
    print "DO RETURN", req, result
    sid = req.session_id
    if sid not in event_hub:
        return False
    result_hub[sid].put(result)
    event_hub[sid].task_done()
    return True

## Controller
class FiscalPrinterController(oeweb.Controller):
    _cp_path = '/fp'

    @oeweb.jsonrequest
    def login(self, req, database, login, password, **kw):
        wsgienv = req.httprequest.environ
        env = dict(
            base_location=req.httprequest.url_root.rstrip('/'),
            HTTP_HOST=wsgienv['HTTP_HOST'],
            REMOTE_ADDR=wsgienv['REMOTE_ADDR'],
        )
        req.session.authenticate(database, login, password, env)
        return {'session_id': req.session_id}

    @oeweb.jsonrequest
    def fp_void(self, req, **kw):
        return do_return(req, {})

    @oeweb.jsonrequest
    def fp_info(self, req, printers, **kw):
        return do_return(req, printers);

    @oeweb.httprequest
    def fp_spool(self, req, **kw):

        sid = req.session_id

        event_hub[sid] = Queue()
        result_hub[sid] = Queue()

        if req.httprequest.headers.get('accept') != 'text/event-stream':
            return req.make_response('Not implemented', status=501)

        def event_source_iter():
            event_id = req.httprequest.headers.get('last-event-id', 0, type=int)

            print "fp_spool:LOOP", sid
            while True:
                print "fp_spool:WAITING"
                item = event_hub[sid].get()
                print "fp_spool:PROCESSING"
                event_id += 1
                message = { 'id': event_id }
                message.update(item)
                yield 'event: %(event)s\ndata: %(data)s\nid: %(id)s\n\n' % message

        def request_info(sid):
            time.sleep(3)
            print "Request info:"
            R  = do_event('info')
            print "Request info:", R
            print R

        p = Process(target=request_info, args=(sid, ))
        p.start()
        print "MAKE RESPONSE!"

        return req.make_response(event_source_iter(),
                                 [('cache-control', 'no-cache'),
                                  ('Content-Type', 'text/event-stream')])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
