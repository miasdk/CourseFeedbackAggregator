"""Simple Zoho OAuth token refresh utility for webhook authentication."""

import requests
import time
from typing import Dict, Optional
from ..config.config import settings


class ZohoTokenService:
    """Simple utility to refresh Zoho OAuth access tokens for webhook validation."""

    def __init__(self):
        self.client_id = settings.zoho_client_id
        self.client_secret = settings.zoho_client_secret
        self.refresh_token = settings.zoho_refresh_token
        self.access_token = settings.zoho_access_token
        self.token_url = "https://accounts.zoho.com/oauth/v2/token"
        self._last_refresh = 0
        self._token_expires_at = 0

    def refresh_access_token(self) -> Dict[str, any]:
        """Refresh the Zoho access token using refresh token."""
        try:
            print("🔄 Refreshing Zoho access token...")

            payload = {
                'refresh_token': self.refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'refresh_token'
            }

            response = requests.post(self.token_url, data=payload, timeout=10)

            if response.status_code == 200:
                token_data = response.json()
                new_access_token = token_data.get('access_token')
                expires_in = token_data.get('expires_in', 3600)

                if new_access_token:
                    # Update token and expiry tracking
                    self.access_token = new_access_token
                    self._last_refresh = time.time()
                    self._token_expires_at = self._last_refresh + expires_in - 300  # 5min buffer

                    print(f"   ✅ Token refresh successful (expires in {expires_in}s)")

                    return {
                        'success': True,
                        'access_token': new_access_token,
                        'expires_in': expires_in,
                        'expires_at': self._token_expires_at
                    }
                else:
                    print("   ❌ No access token in response")
                    return {'success': False, 'error': 'No access token received'}
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('error_description', f'HTTP {response.status_code}')
                print(f"   ❌ Token refresh failed: {error_message}")
                return {'success': False, 'error': error_message}

        except requests.RequestException as e:
            print(f"   ❌ Token refresh request failed: {str(e)}")
            return {'success': False, 'error': f'Request failed: {str(e)}'}
        except Exception as e:
            print(f"   ❌ Token refresh exception: {str(e)}")
            return {'success': False, 'error': str(e)}

    def get_valid_access_token(self) -> Optional[str]:
        """Get a valid access token, refreshing automatically if needed."""
        current_time = time.time()

        # Check if token needs refresh (expired or close to expiring)
        if not self.access_token or current_time >= self._token_expires_at:
            print("🔄 Access token expired or missing, refreshing...")
            refresh_result = self.refresh_access_token()

            if refresh_result.get('success'):
                return self.access_token
            else:
                print(f"❌ Failed to refresh token: {refresh_result.get('error')}")
                return None

        return self.access_token

    def validate_webhook_signature(self, payload: str, signature: str) -> bool:
        """Validate Zoho webhook signature (if implemented by Zoho)."""
        # Note: Zoho Survey webhooks may not provide signature validation
        # This is a placeholder for future implementation
        print("⚠️  Webhook signature validation not implemented yet")
        return True

    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers with valid access token."""
        valid_token = self.get_valid_access_token()
        if valid_token:
            return {
                'Authorization': f'Zoho-oauthtoken {valid_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        else:
            raise Exception("Unable to obtain valid Zoho access token")

    def test_token_validity(self) -> Dict[str, any]:
        """Test if current access token is working."""
        try:
            token = self.get_valid_access_token()
            if not token:
                return {'success': False, 'error': 'No valid token available'}

            headers = {'Authorization': f'Zoho-oauthtoken {token}'}
            response = requests.get(
                'https://www.zohoapis.com/crm/v2/org',
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Token is valid',
                    'expires_in': max(0, int(self._token_expires_at - time.time()))
                }
            else:
                return {
                    'success': False,
                    'error': f'Token validation failed: HTTP {response.status_code}'
                }

        except Exception as e:
            return {
                'success': False,
                'error': f'Token validation exception: {str(e)}'
            }