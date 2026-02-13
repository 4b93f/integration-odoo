import xmlrpc.client
import logging
from .config import settings


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OdooClient:
    def __init__(self, url=None, db=None, username=None, password=None, timeout=10):
        self.url = settings.odoo_url
        self.db = settings.odoo_db
        self.username = settings.odoo_username
        self.password = settings.odoo_password
        self.uid = None
        self.common = None
        self.models = None
        self._connected = False
        
        logger.info(f'Initializing OdooClient for {self.url}')
    
    def connect(self):
        if self._connected:
            return
        try:
            logger.info(f'Connecting to Odoo server at {self.url}')
            
            self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
            
            version = self.common.version()
            self._connected = True
            logger.info(f'Connected successfully. Server version: {version.get("server_version", "unknown")}')
            return version
        except Exception as e:
            self._connected = False
            logger.error(f'Connection failed: {e}')
            raise ConnectionError(f'Failed to connect: {e}')
    
    def authenticate(self):
        if not self._connected:
            logger.error('Not connected. Call connect() first.')
            raise RuntimeError('Not connected. Call connect() first.')
            
        try:
            logger.info(f'Authenticating user: {self.username}')
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})

            if not self.uid:
                logger.error('Authentication failed - invalid credentials')
                raise ValueError('Authentication failed - check credentials')
            logger.info(f'Authentication successful (uid: {self.uid})')

            return self.uid
        except Exception as e:
            logger.error(f'Authentication error: {e}')
            raise AuthenticationError(f'Authentication error: {e}')
    
    def execute(self, model, method, *args):
        if not self.uid:
            logger.error('Attempted to execute without authentication')
            raise RuntimeError('Not authenticated. Call authenticate() first.')
        
        try:
            logger.debug(f'Executing {model}.{method} with args: {args}')
            result = self.models.execute_kw(
                self.db, self.uid, self.password,
                model, method, list(args)
            )

            logger.info(f'Execute successful for {model}.{method}')
            return result
        except Exception as e:
            logger.error(f'API call failed for {model}.{method}: {e}')
            raise RuntimeError(f'API call failed: {e}')
    
    def get_partners(self, fields=None, domain=None):
        domain = []
        params = {}
            
        try:
            result = self.models.execute_kw(
                self.db, self.uid, self.password,
                'res.partner', 'search_read', [domain], params
            )
            logger.debug(f'Retrieved {len(result)} partners')
            return result
        except Exception as e:
            logger.error(f'get_partners failed: {e}')
            raise RuntimeError(f'API call failed: {e}')
        
    def get_fields(self, model):
        if not self.uid:
            self.authenticate()
        models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")
        return models.execute_kw(
            self.db, self.uid, self.password,
            model, "fields_get",
            [],
            {"attributes": ["type", "string"]}            
    )
    


class AuthenticationError(Exception):
    pass

