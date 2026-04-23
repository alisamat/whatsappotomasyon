"""
Kuveyt Türk Sanal POS (3D Secure) Entegrasyonu - XML API v2.0
https://www.kuveytturk.com.tr/

3D Secure Payment Flow:
1. create_3d_payment() -> XML oluştur + 3D Secure başlat
2. User -> Bank 3D Secure sayfası
3. Bank -> OkUrl/FailUrl callback (AuthenticationResponse)
4. verify_3d_callback() -> MD doğrula
5. provision_payment() -> Final ödeme provizyon

API Endpoints:
- 3D Secure Start: https://sanalpos.kuveytturk.com.tr/ServiceGateWay/Home/ThreeDModelPayGate
- Provision: https://sanalpos.kuveytturk.com.tr/ServiceGateWay/Home/ThreeDModelProvisionGate
"""

import hashlib
import base64
import requests
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from flask import current_app as _app

class _Config:
    @property
    def KUVEYTTURK_MERCHANT_ID(self): return _app.config.get('KUVEYTTURK_MERCHANT_ID', '')
    @property
    def KUVEYTTURK_CUSTOMER_ID(self): return _app.config.get('KUVEYTTURK_CUSTOMER_ID', '')
    @property
    def KUVEYTTURK_USERNAME(self): return _app.config.get('KUVEYTTURK_USERNAME', '')
    @property
    def KUVEYTTURK_PASSWORD(self): return _app.config.get('KUVEYTTURK_PASSWORD', '')
    @property
    def BASE_URL(self): return _app.config.get('BASE_URL', '')

Config = _Config()

logger = logging.getLogger(__name__)


def generate_hash_payment(merchant_id, order_id, amount, ok_url, fail_url, username, password):
    """
    3D Secure ödeme başlatma için hash oluşturur

    Hash Format: base64(sha1(MerchantId + MerchantOrderId + Amount + OkUrl + FailUrl + UserName + HashedPassword))
    HashedPassword: base64(sha1(Password))
    """
    # Password hash (ISO-8859-9 encoding - Türkçe karakter desteği)
    hashed_password = base64.b64encode(
        hashlib.sha1(password.encode('iso-8859-9')).digest()
    ).decode('utf-8')

    # Hash string oluştur
    hash_str = f"{merchant_id}{order_id}{amount}{ok_url}{fail_url}{username}{hashed_password}"

    # SHA1 hash
    hash_bytes = hashlib.sha1(hash_str.encode('iso-8859-9')).digest()

    # Base64 encode
    return base64.b64encode(hash_bytes).decode('utf-8')


def generate_hash_provision(merchant_id, order_id, amount, username, password):
    """
    Provision (final ödeme) için hash oluşturur

    Hash Format: base64(sha1(MerchantId + MerchantOrderId + Amount + UserName + HashedPassword))
    """
    # Password hash
    hashed_password = base64.b64encode(
        hashlib.sha1(password.encode('iso-8859-9')).digest()
    ).decode('utf-8')

    # Hash string oluştur
    hash_str = f"{merchant_id}{order_id}{amount}{username}{hashed_password}"

    # SHA1 hash
    hash_bytes = hashlib.sha1(hash_str.encode('iso-8859-9')).digest()

    # Base64 encode
    return base64.b64encode(hash_bytes).decode('utf-8')


def create_3d_payment_xml(card_holder_name, card_number, card_expire_month, card_expire_year,
                          card_cvv, amount, order_id, merchant_id, customer_id, username,
                          password, ok_url, fail_url, client_ip="127.0.0.1"):
    """
    3D Secure için XML oluşturur

    Args:
        card_holder_name: Kart sahibi adı
        card_number: 16 haneli kart numarası
        card_expire_month: Son kullanma ay (MM)
        card_expire_year: Son kullanma yıl (YY)
        card_cvv: CVV2 kodu
        amount: İşlem tutarı (kuruş cinsinden, örn: 1.00 TL = 100)
        order_id: Sipariş numarası
        merchant_id: Mağaza numarası
        customer_id: Müşteri numarası (boş olabilir)
        username: API kullanıcı adı
        password: API şifresi
        ok_url: Başarılı callback URL
        fail_url: Başarısız callback URL
        client_ip: Müşteri IP adresi

    Returns:
        str: XML string
    """
    # Türkçe karakterleri temizle (XML encoding sorunu)
    turkish_map = {
        'Ç': 'C', 'ç': 'c',
        'Ğ': 'G', 'ğ': 'g',
        'İ': 'I', 'ı': 'i',
        'Ö': 'O', 'ö': 'o',
        'Ş': 'S', 'ş': 's',
        'Ü': 'U', 'ü': 'u'
    }
    for tr_char, en_char in turkish_map.items():
        card_holder_name = card_holder_name.replace(tr_char, en_char)

    # Hash oluştur
    hash_data = generate_hash_payment(merchant_id, order_id, amount, ok_url, fail_url, username, password)

    # XML template
    xml = f'''<KuveytTurkVPosMessage xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <APIVersion>TDV2.0.0</APIVersion>
    <OkUrl>{ok_url}</OkUrl>
    <FailUrl>{fail_url}</FailUrl>
    <HashData>{hash_data}</HashData>
    <MerchantId>{merchant_id}</MerchantId>
    <CustomerId>{customer_id}</CustomerId>
    <UserName>{username}</UserName>
    <CardNumber>{card_number}</CardNumber>
    <CardExpireDateYear>{card_expire_year}</CardExpireDateYear>
    <CardExpireDateMonth>{card_expire_month}</CardExpireDateMonth>
    <CardCVV2>{card_cvv}</CardCVV2>
    <CardHolderName>{card_holder_name}</CardHolderName>
    <CardType>MasterCard</CardType>
    <BatchID>0</BatchID>
    <TransactionType>Sale</TransactionType>
    <InstallmentCount>0</InstallmentCount>
    <Amount>{amount}</Amount>
    <DisplayAmount>{amount}</DisplayAmount>
    <CurrencyCode>0949</CurrencyCode>
    <MerchantOrderId>{order_id}</MerchantOrderId>
    <TransactionSecurity>3</TransactionSecurity>
    <DeviceData>
        <DeviceChannel>02</DeviceChannel>
        <ClientIP>{client_ip}</ClientIP>
    </DeviceData>
</KuveytTurkVPosMessage>'''

    return xml


def create_provision_xml(order_id, amount, md, merchant_id, customer_id, username, password):
    """
    Provision (final ödeme) için XML oluşturur

    Args:
        order_id: Sipariş numarası
        amount: İşlem tutarı
        md: 3D Secure'dan dönen MD değeri
        merchant_id: Mağaza numarası
        customer_id: Müşteri numarası
        username: API kullanıcı adı
        password: API şifresi

    Returns:
        str: XML string
    """
    # Hash oluştur
    hash_data = generate_hash_provision(merchant_id, order_id, amount, username, password)

    # XML template
    xml = f'''<KuveytTurkVPosMessage xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <APIVersion>1.0.0</APIVersion>
    <HashData>{hash_data}</HashData>
    <MerchantId>{merchant_id}</MerchantId>
    <CustomerId>{customer_id}</CustomerId>
    <UserName>{username}</UserName>
    <TransactionType>Sale</TransactionType>
    <InstallmentCount>0</InstallmentCount>
    <CurrencyCode>0949</CurrencyCode>
    <Amount>{amount}</Amount>
    <MerchantOrderId>{order_id}</MerchantOrderId>
    <TransactionSecurity>3</TransactionSecurity>
    <KuveytTurkVPosAdditionalData>
        <AdditionalData>
            <Key>MD</Key>
            <Data>{md}</Data>
        </AdditionalData>
    </KuveytTurkVPosAdditionalData>
</KuveytTurkVPosMessage>'''

    return xml


def start_3d_secure_payment(card_holder_name, card_number, card_expire_month, card_expire_year,
                            card_cvv, amount, order_id, client_ip="127.0.0.1", callback_path=None):
    """
    3D Secure ödeme işlemini başlatır

    Args:
        card_holder_name: Kart sahibi adı
        card_number: 16 haneli kart numarası
        card_expire_month: Son kullanma ay (MM)
        card_expire_year: Son kullanma yıl (YY)
        card_cvv: CVV2 kodu
        amount: İşlem tutarı (kuruş cinsinden)
        order_id: Sipariş numarası
        client_ip: Müşteri IP adresi

    Returns:
        dict: {
            success: bool,
            html_content: str (3D Secure HTML page),
            error: str (if failed)
        }
    """
    try:
        # Config'den bilgileri al
        merchant_id = Config.KUVEYTTURK_MERCHANT_ID
        customer_id = Config.KUVEYTTURK_CUSTOMER_ID or ""
        username = Config.KUVEYTTURK_USERNAME
        password = Config.KUVEYTTURK_PASSWORD

        # Callback URL - özel path verilmişse kullan, yoksa default
        if callback_path:
            ok_url = f"{Config.BASE_URL}{callback_path}"
            fail_url = f"{Config.BASE_URL}{callback_path}"
        else:
            ok_url = f"{Config.BASE_URL}/api/payment/kuveytturk/callback"
            fail_url = f"{Config.BASE_URL}/api/payment/kuveytturk/callback"

        if not all([merchant_id, username, password]):
            logger.error("❌ Kuveyt Türk credentials eksik")
            return {
                'success': False,
                'error': 'Ödeme sistemi yapılandırması eksik'
            }

        # XML oluştur
        xml = create_3d_payment_xml(
            card_holder_name, card_number, card_expire_month, card_expire_year,
            card_cvv, amount, order_id, merchant_id, customer_id, username,
            password, ok_url, fail_url, client_ip
        )

        # API'ye gönder (Canlı ortam)
        api_url = "https://sanalpos.kuveytturk.com.tr/ServiceGateWay/Home/ThreeDModelPayGate"

        headers = {
            'Content-Type': 'application/xml',
            'Content-Length': str(len(xml))
        }

        logger.info(f"🏦 Kuveyt Türk 3D Secure başlatılıyor - OrderId: {order_id}, Amount: {amount}")
        logger.info(f"📤 XML (first 500 chars): {xml[:500]}")
        logger.info(f"📤 XML (last 500 chars): {xml[-500:]}")

        response = requests.post(api_url, data=xml, headers=headers, verify=True, timeout=30)

        if response.status_code == 200:
            # Başarılı - 3D Secure HTML sayfası döner
            logger.info(f"✅ 3D Secure başlatıldı - OrderId: {order_id}")
            return {
                'success': True,
                'html_content': response.text,
                'order_id': order_id
            }
        else:
            logger.error(f"❌ 3D Secure başlatma hatası - Status: {response.status_code}")
            return {
                'success': False,
                'error': f'Ödeme başlatılamadı (HTTP {response.status_code})'
            }

    except Exception as e:
        logger.error(f"❌ Kuveyt Türk 3D Secure error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            'success': False,
            'error': 'Ödeme başlatılamadı'
        }


def parse_3d_callback_xml(xml_string):
    """
    3D Secure callback XML'ini parse eder

    Args:
        xml_string: AuthenticationResponse XML

    Returns:
        dict: Parsed values
    """
    try:
        root = ET.fromstring(xml_string)

        # ResponseCode ve ResponseMessage (root level)
        response_code = root.find('ResponseCode').text if root.find('ResponseCode') is not None else None
        response_message = root.find('ResponseMessage').text if root.find('ResponseMessage') is not None else None

        # VPosMessage içindeki değerler
        vpos_msg = root.find('VPosMessage')

        # VPosMessage varsa içindeki değerleri al
        if vpos_msg is not None:
            result = {
                'response_code': response_code,
                'response_message': response_message,
                'merchant_order_id': vpos_msg.find('MerchantOrderId').text if vpos_msg.find('MerchantOrderId') is not None else None,
                'order_id': vpos_msg.find('OrderId').text if vpos_msg.find('OrderId') is not None else None,
                'provision_number': vpos_msg.find('ProvisionNumber').text if vpos_msg.find('ProvisionNumber') is not None else None,
                'rrn': vpos_msg.find('RRN').text if vpos_msg.find('RRN') is not None else None,
                'stan': vpos_msg.find('Stan').text if vpos_msg.find('Stan') is not None else None,
                'amount': vpos_msg.find('Amount').text if vpos_msg.find('Amount') is not None else None,
                'hash_data': vpos_msg.find('HashData').text if vpos_msg.find('HashData') is not None else None,
                'md': root.find('MD').text if root.find('MD') is not None else None
            }
        else:
            # VPosMessage yoksa (hata durumunda), sadece root level bilgiler
            logger.warning(f"⚠️ VPosMessage not found in XML. ResponseCode: {response_code}, ResponseMessage: {response_message}")
            result = {
                'response_code': response_code,
                'response_message': response_message,
                'merchant_order_id': None,
                'order_id': None,
                'provision_number': None,
                'rrn': None,
                'stan': None,
                'amount': None,
                'hash_data': None,
                'md': None
            }

        return result

    except Exception as e:
        logger.error(f"❌ XML parse error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def verify_3d_callback(authentication_response):
    """
    3D Secure callback'ini doğrular

    Args:
        authentication_response: POST'tan gelen AuthenticationResponse (URL encoded XML)

    Returns:
        dict: {
            success: bool,
            order_id: str,
            amount: str,
            md: str (provision için gerekli),
            error: str (if failed)
        }
    """
    try:
        from urllib.parse import unquote_plus

        # URL decode (1 kere - PHP örneğinde de 1 kere decode ediliyor)
        # unquote_plus: + karakterini space'e çevirir
        xml_string = unquote_plus(authentication_response)

        logger.info(f"📄 Decoded XML (first 500 chars): {xml_string[:500]}")

        # XML parse
        parsed = parse_3d_callback_xml(xml_string)

        if not parsed:
            return {
                'success': False,
                'error': 'XML parse hatası'
            }

        # ResponseCode "00" ve ResponseMessage "Kart doğrulandı" kontrolü
        if parsed['response_code'] == '00' and 'doğrulandı' in parsed['response_message'].lower():
            logger.info(f"✅ 3D Secure doğrulama başarılı - OrderId: {parsed['merchant_order_id']}, MD: {parsed['md']}")
            return {
                'success': True,
                'order_id': parsed['merchant_order_id'],
                'amount': parsed['amount'],
                'md': parsed['md'],
                'provision_number': parsed['provision_number'],
                'rrn': parsed['rrn']
            }
        else:
            logger.error(f"❌ 3D Secure doğrulama başarısız - Code: {parsed['response_code']}, Message: {parsed['response_message']}")
            return {
                'success': False,
                'error': f"3D Secure doğrulama başarısız: {parsed['response_message']}"
            }

    except Exception as e:
        logger.error(f"❌ Kuveyt Türk callback verification error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            'success': False,
            'error': 'Ödeme doğrulama hatası'
        }


def provision_payment(order_id, amount, md):
    """
    Final ödeme provision işlemi (3D Secure doğrulaması sonrası)

    Args:
        order_id: Sipariş numarası
        amount: İşlem tutarı
        md: 3D Secure'dan dönen MD değeri

    Returns:
        dict: {
            success: bool,
            provision_number: str,
            rrn: str,
            error: str (if failed)
        }
    """
    try:
        # Config'den bilgileri al
        merchant_id = Config.KUVEYTTURK_MERCHANT_ID
        customer_id = Config.KUVEYTTURK_CUSTOMER_ID or ""
        username = Config.KUVEYTTURK_USERNAME
        password = Config.KUVEYTTURK_PASSWORD

        # XML oluştur
        xml = create_provision_xml(order_id, amount, md, merchant_id, customer_id, username, password)

        # API'ye gönder (Canlı ortam)
        api_url = "https://sanalpos.kuveytturk.com.tr/ServiceGateWay/Home/ThreeDModelProvisionGate"

        headers = {
            'Content-Type': 'application/xml',
            'Content-Length': str(len(xml))
        }

        logger.info(f"💳 Provision başlatılıyor - OrderId: {order_id}")

        response = requests.post(api_url, data=xml, headers=headers, verify=True, timeout=30)

        if response.status_code == 200:
            # XML parse
            root = ET.fromstring(response.text)
            response_code = root.find('.//ResponseCode').text if root.find('.//ResponseCode') is not None else None

            if response_code == '00':
                provision_number = root.find('.//ProvisionNumber').text if root.find('.//ProvisionNumber') is not None else None
                rrn = root.find('.//RRN').text if root.find('.//RRN') is not None else None

                logger.info(f"✅ Provision başarılı - OrderId: {order_id}, ProvisionNumber: {provision_number}")
                return {
                    'success': True,
                    'provision_number': provision_number,
                    'rrn': rrn,
                    'order_id': order_id
                }
            else:
                response_message = root.find('.//ResponseMessage').text if root.find('.//ResponseMessage') is not None else 'Bilinmeyen hata'
                logger.error(f"❌ Provision başarısız - Code: {response_code}, Message: {response_message}")
                return {
                    'success': False,
                    'error': f'Ödeme alınamadı: {response_message}'
                }
        else:
            logger.error(f"❌ Provision hatası - Status: {response.status_code}")
            return {
                'success': False,
                'error': f'Ödeme alınamadı (HTTP {response.status_code})'
            }

    except Exception as e:
        logger.error(f"❌ Provision error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            'success': False,
            'error': 'Ödeme alınamadı'
        }
