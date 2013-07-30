#!/usr/bin/env python

"""
    RESTful INSIKA HTTP Test Server

    Copyright (c) 2013 Physikalisch-Technische Bundesanstalt (PTB)
    Abbestr. 2-12, 10587 Berlin, Germany
    http://insika.de/

    NOTE: This server is designed for development and conformance tests on 
    application level only. Do not use in productive environments!

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License version 2
    as published by the Free Software Foundation.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


    ToDo:
    - check Status Codes
    - Serverlist as shelve
    - key validation for every particular key
    - XML parsing, validation, XML export
    - SSL support (see web.py cookbook)

    using some parts from John Paulett:
    http://johnpaulett.com/2008/09/20/getting-restful-with-webpy/
    based on web.py: http://webpy.org/

"""

import os
import re
import shelve
import web
from   time import strftime
import time
import string

VALID_KEY    = re.compile('[A-Z0-9_-]{1,16}')

urls = (
    '/insika/servers', 'Servers',
    '/insika/(.*)/(.*)/servers', 'ServersPersonal',
    '/insika/(.*)/(.*)/init', 'Init', 
    '/insika/(.*)/(.*)/(.*)/(.*)', 'Insika',
    '/(.*)', 'Index'
)


def is_valid_key(key):
    if VALID_KEY.match(key) is not None:
        return True
    return False


def validate_key(fn):
    def new(*args):
        if not is_valid_key(args[1]):
            web.webapi.debug('bad request in validate key')
            web.webapi.badrequest()
        return fn(*args)
    return new


def log_msg():
    local_time = strftime('%Y-%m-%d %H:%M:%S')
    msg = ( ' Server-Time    : ' + str(local_time) + '<br />' +
            '>> Request' + '<br />' +
            ' IP-Address     : ' + str(web.ctx.ip) + '<br />' +
            ' Request-Method : ' + web.ctx.env['REQUEST_METHOD'] + '<br />' +
            #'Script-Name    : ' + web.ctx.env['SCRIPT_NAME'] + '<br />' +
            ' Path-Info      : ' + web.ctx.env['PATH_INFO'] + '<br />' +
            ' Content-Type   : ' + web.ctx.env['CONTENT_TYPE'] + '<br />' +
            ' Content-Length : ' + web.ctx.env['CONTENT_LENGTH'] + '<br />' +
            ' Protocol       : ' + web.ctx.env['SERVER_PROTOCOL'] +'<br />' +
            #' HTTP-Accept    : ' + web.ctx.env['HTTP_ACCEPT'] +'<br />' +
            #' HTTP-User-Agent: ' + web.ctx.env['HTTP_USER_AGENT'] +'<br />' +
            ' Message-Body  -> ' + ''.join(['<a href="',web.ctx.env['PATH_INFO'],'">',web.ctx.env['PATH_INFO'],'</a><br />']) +
            '<< Response' + '<br />' + 
            ' Status-Code    : ' + web.ctx.status + '<br />' +
            ' Body (opt.)    : ' + web.ctx.output )
    try:
        # logging
        log_db = shelve.open('log.db', writeback=True)
        lt = int(time.time()*100)
        log_db[str(lt)] = msg
        log_db.sync()
    except:
        web.webapi.debug('Logging failed')
    return
  

class Servers(object):
    """ Servers class for serverlist
    """
    def GET(self):
        try:
          server = open('serverlist/serverlist.txt', 'r')
          return server
        except:
          web.webapi.notfound()
          return
        

class ServersPersonal(object):
    """ ServersPersonal class for personal serverlist
    """
    @validate_key    
    def GET(self, tpId, tpIdNo):
        raise web.webapi.seeother('/insika/servers')
        return


class Init(object):
    """ Init class for initialisation of TIM on server
    """
    @validate_key
    def POST(self, tpId, tpIdNo):
        tpIdList = os.listdir('db')
        if tpId in tpIdList:
            web.webapi.debug(tpId)
            tpIdNoList = os.listdir('db/' + tpId)
            web.webapi.debug(tpIdNoList)
            if tpIdNo in tpIdNoList:
                web.webapi.debug('TPID found!')
            else:
                # register new tpIdNo
                os.mkdir('db/' + tpId + '/' + tpIdNo)
            # log message
            data = web.webapi.data()
            # sanity check for elements 'insika' and 'xml'
            if data.find('xml') == -1 or data.find('insika') == -1:
                web.webapi.debug('bad request in sanity check')                    
                return web.webapi.badrequest()
            try:
                i = Insika()
                i.POST(tpId, tpIdNo, 'init', '1')                    
            except:
                web.webapi.internalerror()      
            log_msg()
            return
        return web.webapi.forbidden()

    @validate_key
    def GET(self, tpId, tpIdNo):
        try:
            new_path = '/'.join(['/insika', tpId, tpIdNo, 'init', '1'])
            web.webapi.seeother(new_path)
        except:
            web.webapi.internalerror()      


class Index(object):
    """ Index class for logging page
    """
    def GET(self, key):
        render = web.template.render('templates/', base='layout')
        try:
            log_db = shelve.open('log.db', writeback=False)
        except:
            return web.webapi.internalerror()
        if key == '':
            keyList = sorted(log_db.keys(), reverse=True)
            tpIdList = os.listdir('db')
            userList = []
            for tpId in tpIdList:
                tpIdNo = os.listdir('db/' + tpId)
                userList.append(tpId)
                userList.append(tpIdNo)
            return render.index(userList, log_db, keyList) 
        else:
            if str(key) in log_db:
                # parse link to message body  
                mbLink = str(log_db[str(key)])
                mbLink = mbLink.partition('<a href=\"/')[2]
                mbLink = mbLink.partition('\">')[0]
                return render.message(log_db, str(key), mbLink)
            else:
                return web.webapi.notfound()
        return
    

class Insika(object):
    """ Insika Class for GET and POST handling
    """
    @validate_key
    def GET(self, tpId, tpIdNo, mode, seqNo):
        db_name = os.path.join('db', tpId, tpIdNo, mode + '.db')
        web.webapi.debug(db_name)
        try:
            database = shelve.open(db_name, writeback=False)
            if len(seqNo) <= 0:
                out = '<html><body><b>Keys:</b><br />'
                for key in sorted(database.iterkeys(), reverse=True):
                    out += ''.join(['<a href="',str(key),'">',str(key),'</a><br />'])
                out += '</body></html>'
                web.webapi.header('Content-Type', 'text/html')
            else:
                key = str(seqNo)
                out = database[key]
                web.webapi.header('Content-Type', 'text/xml')
            return out
        except:
            web.webapi.notfound()
        return

    @validate_key
    def POST(self, tpId, tpIdNo, mode, seqNo):
        data = web.webapi.data()
        # sanity check for elements 'insika' and 'xml'
        if data.find('xml') == -1 or data.find('insika') == -1:
            web.webapi.debug('bad request in sanity check')                    
            return web.webapi.badrequest()
        db_name = os.path.join('db', tpId, tpIdNo, mode + '.db')
        try:
            database = shelve.open(db_name, writeback=True)
            key = str(seqNo)
            database[key] = data
            database.sync()
            # response
            web.webapi.created()
        except:
            web.webapi.internalerror()
        log_msg()
        return
    

if __name__ == "__main__":
    web.config.debug = False
    app = web.application(urls, globals())
    app.run()
