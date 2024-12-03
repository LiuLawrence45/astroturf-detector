import socket
import socks
import requests

class ProxyHandler:
    def __init__(self):
        self.original_socket = socket.socket

    def get_new_proxy(self):
        """Generate new proxy credentials for each request"""
        return {
            'host': 'gw.dataimpulse.com',
            'port': 823,
            'username': '272fa0a72b6a0f39e1f4',
            'password': '7dae8f8fcce7d3db'
        }

    def test_proxy(self, proxy):
        """Test if proxy works by checking IP"""
        original_socket = socket.socket
        try:
            socks.set_default_proxy(
                socks.SOCKS5, 
                proxy['host'],
                proxy['port'],
                username=proxy['username'],
                password=proxy['password']
            )
            socket.socket = socks.socksocket
            ip = requests.get('https://api.ipify.org').text
            print(f"Using proxy IP: {ip}")
            return True
        except Exception as e:
            print(f"Proxy test failed: {e}")
            return False
        finally:
            socket.socket = original_socket

    def assign_new_proxy(self):
        """Assign and configure a new proxy"""
        proxy = self.get_new_proxy()
        if self.test_proxy(proxy):
            # If test successful, set up the proxy for actual use
            socks.set_default_proxy(
                socks.SOCKS5, 
                proxy['host'],
                proxy['port'],
                username=proxy['username'],
                password=proxy['password']
            )
            socket.socket = socks.socksocket
            return True
        return False