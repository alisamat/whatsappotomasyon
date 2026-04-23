"""
BASE SEKTÖR HANDLER — tüm sektörler bu sınıftan türer
"""
from abc import ABC, abstractmethod


class BaseSektorHandler(ABC):
    """
    Her sektör bu sınıfı implement eder.

    Kullanıcıdan gelen mesajlar bir "oturum" (session) içinde
    toplanır: fotoğraflar, konum, kişi bilgisi gibi.

    Yeterli veri gelince handle() belgeyi üretir ve gönderir.
    """

    # Alt sınıfta override edilmeli
    SEKTOR_KODU   = ''         # 'emlak', 'marangoz', ...
    KREDI_MALIYETI = 3         # işlem başına kredi
    MIN_FOTOGRAF  = 1
    MAX_FOTOGRAF  = 5

    @abstractmethod
    def handle(self, telefon: str, session: dict,
               phone_number_id: str, access_token: str) -> bool:
        """
        Session yeterli veriye sahipse işlemi tamamla ve True döndür.
        Henüz veri eksikse yönlendirici mesaj gönder, False döndür.
        """
        ...

    @abstractmethod
    def session_tamam_mi(self, session: dict) -> bool:
        """Session işlem için yeterli mi?"""
        ...

    def beklenen_veri_mesaji(self) -> str:
        """Kullanıcıya ne göndermesi gerektiğini anlatan mesaj."""
        return 'Lütfen gerekli bilgileri gönderin.'

    def mesaj_isle(self, telefon: str, mesaj: dict, session: dict,
                   phone_number_id: str, access_token: str, user) -> bool:
        """State machine mesaj işleyici. Tamamlanınca True döner. Alt sınıflar override eder."""
        return False
