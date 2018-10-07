import logging
import xmlrpc.client as xmlrpclib

_logger = logging.getLogger(__name__)


class ProxiedTransport(xmlrpclib.Transport):
    # Put here an identification string for your application
    user_agent = 'RFID Attendance Terminal'

    def set_proxy(self, proxy):
        self.proxy = proxy

    def make_connection(self, host):
        self.realhost = host
        import http.client as httplib
        return httplib.HTTPConnection(self.proxy)

    def send_request(self, connection, handler, request_body):
        connection.putrequest("POST", 'http://%s%s' % (self.realhost, handler))

    def send_host(self, connection, host):
        connection.putheader('Host', self.realhost)

    def __init__(self, proxy, use_datetime=0):
        xmlrpclib.Transport.__init__(self, use_datetime)
        self.set_proxy(proxy)


class OdooXmlRPC(object):
    
    def __init__(self, host, port, https_on, db, user, pswd, proxy):
        
        self.db = db
        self.user = user
        self.pswd = pswd

        # TODO Analyze case HTTPS and port diferent from 443
        if https_on and port is None:
            self.url_template = ("https://%s/xmlrpc/" % host)
        elif https_on and port:
            self.url_template = ("https://%s:%s/xmlrpc/" % (host, port))
        elif port:
            self.url_template = ("http://%s:%s/xmlrpc/" % (host, port))
        else:
            self.url_template = ("http://%s/xmlrpc/" % host)
        self.uid = self._get_user_id()

    def _get_object_facade(self, url, proxy=None):
        _logger.debug("Creating object_facade")
        if proxy:
            object_facade = xmlrpclib.ServerProxy(
                self.url_template + str(url),
                transport=ProxiedTransport(proxy)
            )
        else:
            object_facade = xmlrpclib.ServerProxy(
                self.url_template + str(url))

        return object_facade

    def _get_user_id(self):
        _logger.debug("Validating Connection to Odoo via XMLRPC")
        login_facade = self._get_object_facade('common')
        try:
            user_id = login_facade.login(self.db, self.user, self.pswd)
            if user_id:
                _logger.debug(
                    "Odoo Connection succed on XMLRPC user %s", str(user_id))
                return user_id
            _logger.debug("Odoo Connection can't return user_id")
            return False
        except Exception:
            _logger.debug("Odoo Connection can't return user_id")
            return False

    def check_attendance(self, card):
        try:
            object_facade = self._get_object_facade('object')
            res = object_facade.execute(
                self.db, self.uid, self.pswd, "hr.employee",
                "register_attendance", card)
            _logger.debug(res)
            return res
        except Exception as e:
            _logger.debug("check_attendance exception request: "+ str(e))
            return False
