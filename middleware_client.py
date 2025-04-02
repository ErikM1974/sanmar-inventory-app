#!/usr/bin/env python
"""
Middleware client for interacting with SanMar SOAP APIs.
"""

import logging
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Import zeep for SOAP client
try:
    from zeep import Client
    from zeep.transports import Transport
    ZEEP_AVAILABLE = True
except ImportError:
    ZEEP_AVAILABLE = False
    logging.warning("Zeep library not available. SOAP API functionality will be limited.")

logger = logging.getLogger(__name__)

def create_session_with_retries(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
    """Create a requests session with retry capabilities."""
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def create_soap_client(wsdl_url, retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
    """Create a SOAP client with retry capabilities."""
    if not ZEEP_AVAILABLE:
        raise ImportError("Zeep library is required for SOAP API functionality.")
    
    session = create_session_with_retries(retries, backoff_factor, status_forcelist)
    transport = Transport(session=session)
    client = Client(wsdl_url, transport=transport)
    return client

def categorize_error(exception):
    """Categorize an exception into a more user-friendly error type and message."""
    # Check if it's a requests exception
    if isinstance(exception, requests.exceptions.RequestException):
        if isinstance(exception, requests.exceptions.ConnectionError):
            return "Connection Error", "Failed to connect to the API server. Please check your internet connection."
        elif isinstance(exception, requests.exceptions.Timeout):
            return "Timeout Error", "The API request timed out. Please try again later."
        elif isinstance(exception, requests.exceptions.HTTPError):
            status_code = exception.response.status_code
            if status_code == 401:
                return "Authentication Error", "Invalid credentials. Please check your username and password."
            elif status_code == 403:
                return "Authorization Error", "You don't have permission to access this resource."
            elif status_code == 404:
                return "Not Found Error", "The requested resource was not found."
            elif status_code == 429:
                return "Rate Limit Error", "You've exceeded the API rate limit. Please try again later."
            elif 500 <= status_code < 600:
                return "Server Error", f"The API server encountered an error (status code: {status_code})."
            else:
                return "HTTP Error", f"HTTP error occurred (status code: {status_code})."
        else:
            return "Request Error", str(exception)
    
    # Check if it's a zeep exception
    if str(exception.__class__).find('zeep') != -1:
        if str(exception).find('authentication') != -1 or str(exception).find('Authentication') != -1:
            return "Authentication Error", "Invalid credentials. Please check your username and password."
        elif str(exception).find('timeout') != -1 or str(exception).find('Timeout') != -1:
            return "Timeout Error", "The SOAP request timed out. Please try again later."
        elif str(exception).find('schema') != -1 or str(exception).find('Schema') != -1:
            return "Schema Error", "The SOAP request does not match the expected schema."
        else:
            return "SOAP Error", str(exception)
    
    # Generic error handling
    return "Error", str(exception)

def retry_on_failure(func, max_retries=3, retry_delay=1, *args, **kwargs):
    """Retry a function on failure with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_type, error_message = categorize_error(e)
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)
                logger.warning(f"{error_type} on attempt {attempt + 1}/{max_retries}: {error_message}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logger.error(f"{error_type} on final attempt: {error_message}")
                raise
