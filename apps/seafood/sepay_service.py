"""
SePay Payment Gateway Integration Service
"""
import requests
from decimal import Decimal
from typing import Dict, Any, Optional
from django.conf import settings


class SepayAPIError(Exception):
    """Custom exception for SePay API errors"""
    pass


class SepayService:
    """
    Service class for integrating with SePay payment gateway
    """

    def __init__(self):
        self.base_url = getattr(settings, 'SEPAY_BASE_URL', 'https://api.sepay.vn')
        self.api_key = getattr(settings, 'SEPAY_API_KEY', '')
        self.account_number = getattr(settings, 'SEPAY_ACCOUNT_NUMBER', '116096779')
        self.account_name = getattr(settings, 'SEPAY_ACCOUNT_NAME', 'TO TRONG HIEU')
        self.bank_code = getattr(settings, 'SEPAY_BANK_CODE', 'BIDV')

    def create_qr_code(
        self,
        amount: Decimal,
        content: str,
        bank_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create VietQR code via SePay API

        Args:
            amount: Transaction amount
            content: Transfer description (e.g., "Thanh toan ORD123")
            bank_code: Bank code (default: BIDV)

        Returns:
            Dictionary with QR code data:
            {
                'account_number': str,
                'account_name': str,
                'qr_image_url': str,
                'qr_svg': str,
                'session_id': str,
                'bank_code': str
            }
        """
        if not self.api_key:
            # Return mock data if no API key configured
            return self._get_mock_qr_data(amount, content, bank_code or self.bank_code)

        url = f"{self.base_url}/api/v1/qr"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'accountNumber': self.account_number,
            'bankCode': bank_code or self.bank_code,
            'amount': str(amount),
            'content': content,
            'template': 'vietqr'
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()

            if data.get('status') == 'success':
                return {
                    'account_number': data.get('accountNumber', self.account_number),
                    'account_name': data.get('accountName', self.account_name),
                    'qr_image_url': data.get('qrCode', ''),
                    'qr_svg': data.get('qrSVG', ''),
                    'session_id': data.get('sessionId', ''),
                    'bank_code': bank_code or self.bank_code
                }
            else:
                raise SepayAPIError(f"SePay API error: {data.get('message', 'Unknown error')}")

        except requests.RequestException as e:
            raise SepayAPIError(f"Failed to create QR code: {str(e)}")

    def _get_mock_qr_data(
        self,
        amount: Decimal,
        content: str,
        bank_code: str
    ) -> Dict[str, Any]:
        """
        Return mock QR data when API key is not configured
        Uses VietQR's free image generation service
        """
        # Get bank ID from bank code
        bank_ids = {
            'BIDV': '970418',
            'VCB': '970436',
            'VTB': '970415',
            'ACB': '970416',
            'TCB': '970407',
            'MB': '970422',
        }
        bank_id = bank_ids.get(bank_code, '970418')

        # Generate VietQR URL
        from urllib.parse import urlencode
        params = {
            'amount': str(amount),
            'addInfo': content,
            'accountName': self.account_name
        }
        qr_url = f"https://img.vietqr.io/image/{bank_id}-{self.account_number}-compact2.png?{urlencode(params)}"

        return {
            'account_number': self.account_number,
            'account_name': self.account_name,
            'qr_image_url': qr_url,
            'qr_svg': '',
            'session_id': '',
            'bank_code': bank_code
        }

    def check_transaction(
        self,
        session_id: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Check transaction history from SePay

        Args:
            session_id: Session ID from QR creation
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            limit: Number of records to fetch

        Returns:
            Dictionary with transaction data
        """
        if not self.api_key:
            return {'status': 'error', 'message': 'API key not configured'}

        url = f"{self.base_url}/api/v1/transactions"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        params = {
            'limit': limit
        }
        if session_id:
            params['sessionId'] = session_id
        if from_date:
            params['fromDate'] = from_date
        if to_date:
            params['toDate'] = to_date

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise SepayAPIError(f"Failed to check transactions: {str(e)}")


# Singleton instance
_sepay_service = None

def get_sepay_service() -> SepayService:
    """Get singleton instance of SepayService"""
    global _sepay_service
    if _sepay_service is None:
        _sepay_service = SepayService()
    return _sepay_service
