import xmlrpc.client
import logging
from typing import List, Dict, Any, Optional
from .config import settings

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Exception raised for errors during Odoo authentication."""
    pass


class OdooClient:
    def __init__(
        self, 
        url: Optional[str] = None, 
        db: Optional[str] = None, 
        username: Optional[str] = None, 
        password: Optional[str] = None
    ):
        self.url = url or settings.odoo_url
        self.db = db or settings.odoo_db
        self.username = username or settings.odoo_username
        self.password = password or settings.odoo_password
        self.uid = None
        self.common = None
        self.models = None
        self._connected = False

    def connect(self) -> Dict[str, Any]:
        """Connect to the Odoo XML-RPC server."""
        if self._connected:
            return {}
        
        try:
            logger.info(f"Connecting to Odoo server at {self.url}")
            # Use allow_none=True to handle None values in XML-RPC calls
            self.common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common", allow_none=True)
            self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object", allow_none=True)
            
            version = self.common.version()
            self._connected = True
            logger.info(f"Connected successfully. Server version: {version.get('server_version', 'unknown')}")
            return version
        except Exception as e:
            self._connected = False
            logger.error(f"Connection failed: {e}")
            raise ConnectionError(f"Failed to connect to Odoo: {e}")

    def authenticate(self) -> int:
        """Authenticate with the Odoo server and return the user ID."""
        if not self._connected:
            self.connect()
            
        try:
            logger.info(f"Authenticating user: {self.username}")
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})

            if not self.uid:
                logger.error("Authentication failed - invalid credentials")
                raise AuthenticationError("Invalid Odoo credentials")
            
            logger.info(f"Authentication successful (uid: {self.uid})")
            return self.uid
        except Exception as e:
            if isinstance(e, AuthenticationError):
                raise
            logger.error(f"Authentication error: {e}")
            raise AuthenticationError(f"Odoo authentication failed: {e}")

    def execute(self, model: str, method: str, *args, **kwargs) -> Any:
        """Execute a method on an Odoo model."""
        if not self.uid:
            self.authenticate()
        
        try:
            return self.models.execute_kw(
                self.db, self.uid, self.password,
                model, method, args, kwargs
            )
        except Exception as e:
            logger.error(f"Odoo API call failed for {model}.{method}: {e}")
            raise RuntimeError(f"Odoo API call failed: {e}")

    def get_partners(self, domain: Optional[List[Any]] = None, fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Fetch partners from Odoo."""
                
        return self.execute("res.partner", "search_read", domain, fields=fields)

    def get_invoices(self, domain: Optional[List[Any]] = None, fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Fetch invoices from Odoo."""
                
        return self.execute("account.move", "search_read", domain, fields=fields)

    def get_fields(self, model: str) -> Dict[str, Any]:
        """Get field definitions for a specific model."""
        return self.execute(model, "fields_get", attributes=["type", "string"])

