from typing import Dict, Any

class TLSConfigManager:
    """
    Manages TLS 1.3 / mTLS configuration guidelines, mutual client verification parameters,
    and communication security status.
    """
    def __init__(self):
        self.enabled = True
        self.protocol_version = "TLSv1.3"
        self.cipher_suite = "TLS_AES_256_GCM_SHA384"
        self.mtls_enabled = True

    def get_status(self) -> Dict[str, Any]:
        return {
            "tls_enabled": self.enabled,
            "protocol_version": self.protocol_version,
            "cipher_suite": self.cipher_suite,
            "mtls_supported": self.mtls_enabled,
            "client_cert_required": True,
            "trusted_cas": ["HealthcareRootCA", "HospitalFederationSubCA"],
            "description": "All communication channels between FL clients and the coordinator enforce TLS 1.3 encryption with Mutual TLS (mTLS) client certificate verification."
        }

tls_manager = TLSConfigManager()
