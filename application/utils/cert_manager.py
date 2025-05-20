import ssl
import certifi
import os
import sys


class CertManager:
    @staticmethod
    def get_certifi_path():
        """
        Return path to certifi. Also working with PyInstaller.
        """
        # If pyinstaller
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
            possible_path = os.path.join(base_path, "certifi", "cacert.pem")
            if os.path.exists(possible_path):
                return possible_path
        # else
        return certifi.where()

    @staticmethod
    def get_ssl_context():
        """
        Create and return SSL context with certificate authority.
        """
        cafile = CertManager.get_certifi_path()
        context = ssl.create_default_context(cafile=cafile)
        return context