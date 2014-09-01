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

from Queue import Queue, Full, Empty
import logging

_logger = logging.getLogger(__name__)

access_control_allow_origin = 'chrome-extension://gileacnnoefamnjnhjnijommagpamona'
event_id = 0
event_hub = {}
result_hub = {}

## Monkey path for HttpRequest
http_old_dispatch = oeweb.HttpRequest.dispatch

def http_dispatch(self):
    r = http_old_dispatch(self)
    if hasattr(r, 'headers'):
        r.headers._list.append(('Access-Control-Allow-Origin',access_control_allow_origin))
        r.headers._list.append(('Access-Control-Allow-Credentials', 'true'))
    return r

oeweb.HttpRequest.dispatch = http_dispatch

## Monkey path for JsonRequest
json_old_dispatch = oeweb.JsonRequest.dispatch

def json_dispatch(self):
    r = json_old_dispatch(self)
    if hasattr(r, 'headers'):
        r.headers._list.append(('Access-Control-Allow-Origin',access_control_allow_origin))
        r.headers._list.append(('Access-Control-Allow-Credentials', 'true'))
    return r

oeweb.JsonRequest.dispatch = json_dispatch

## Event manager
def do_event(event, data={}, session_id=None, printer_id=None, control=False):
    event_result = {}
    item = {
        'event': event,
        'data': json.dumps(data),
    }

    # Select target of queue. Control go to Chrome Application, else take printers.
    # All control queue end with ':'.
    if control:
        qids = [ session_id ] if session_id else [ qid for qid in event_hub.keys() if qid[-1] == ':']
    else:
        qid = ':'.join([session_id or '', printer_id or ''])
        qids = [ qid ] if qid != ':' else event_hub.keys()
        qids = [ qid for qid in qids if qid in event_hub.keys() and qid[-1] != ':' ]

    _logger.debug("Send message '%s' to spools: %s" % (event, qids))

    for qid in qids:
        try:
            event_hub[qid].put(item, True, 10)
            r = result_hub[qid].get()
            result_hub[qid].task_done()
            event_result[qid] = r
        except Full:
            _logger.warning("Queue put timeout for session %s:" % qid)
            pass
        except:
            _logger.error("Unexpected error for session %s:" % qid, sys.exc_info()[0])
            raise

    return [ event_result[qid] for qid in qids if qid in event_result ]

def do_return(req, result):
    sid = req.session_id
    pid = req.params.get('printer_id', '')
    qid = ':'.join([sid, pid])

    if qid not in event_hub:
        return False

    result_hub[qid].put(result)
    _logger.debug("<<< QID: %s" % qid)
    event_hub[qid].task_done()
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
    def push(self, req, **kw):
        return do_return(req, kw)

    @oeweb.httprequest
    def spool(self, req, **kw):
        sid = req.session_id
        pid = req.params.get('printer_id', '')
        qid = ':'.join([sid, pid])

        _logger.debug("Create new spool: %s" % qid)

        if (qid in event_hub):
            del event_hub[qid]
            del result_hub[qid]

        event_hub[qid] = Queue()
        result_hub[qid] = Queue()

        if req.httprequest.headers.get('accept') != 'text/event-stream':
            return req.make_response('Not implemented', headers={'Status': '501 Not Implemented'})

        def event_source_iter():
            event_id = req.httprequest.headers.get('last-event-id', 0, type=int)

            while True:
                item = event_hub[qid].get()
                event_id += 1
                message = { 'id': event_id }
                message.update(item)
                _logger.debug("Send message %s to %s" % (item['event'], qid))
                yield 'event: %(event)s\ndata: %(data)s\nid: %(id)s\n\n' % message

        return req.make_response(event_source_iter(),
                                 [('cache-control', 'no-cache'),
                                  ('Content-Type', 'text/event-stream')])

    @oeweb.jsonrequest
    def fp_info(self, req, printers, **kw):
        return do_return(req, printers);

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
