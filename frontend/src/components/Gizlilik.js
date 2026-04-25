import React from 'react';
import Layout from './Layout';

const SORUMLU = {
  unvan:   'Promis Web Hizmetleri Emlak Gıda Ticaret ve Limited Şirketi',
  mersis:  '0733038351000014',
  adres:   'Göktürk Merkez Mah. Belediye Cd. Tontaş İşmerkezi No:16 Eyüp/İstanbul',
  eposta:  'admin@onmuhasebeci.com.tr',
  tel:     '(0212) 322 17 22',
  web:     'www.onmuhasebeci.net',
};

const MADDELER = [
  {
    baslik: '1. Veri Sorumlusu',
    metin: `6698 sayılı Kişisel Verilerin Korunması Kanunu ("KVKK") kapsamında veri sorumlusu sıfatıyla hareket eden şirketimiz:

Unvan: ${SORUMLU.unvan}
MERSİS: ${SORUMLU.mersis}
Adres: ${SORUMLU.adres}
E-posta: ${SORUMLU.eposta}
Telefon: ${SORUMLU.tel}`,
  },
  {
    baslik: '2. İşlenen Kişisel Veriler ve İşleme Amaçları',
    metin: `a) Hizmet kullanıcıları (emlakçılar): Ad-soyad, e-posta, telefon numarası, sektör bilgisi — üyelik oluşturma, kimlik doğrulama, kredi ve abonelik yönetimi, faturalandırma amacıyla işlenmektedir.

b) Alıcı/kiracı adayları (3. kişiler): Ad-soyad, TC kimlik numarası (isteğe bağlı), telefon numarası, adres bilgisi — yer gösterme sözleşmesi belgesi oluşturulması amacıyla işlenmektedir. Bu veriler kullanıcı tarafından sisteme girilmekte olup sözleşme belgesi ilgili kullanıcıya iletilmektedir.

c) Ödeme bilgileri: Kredi kartı verileri yalnızca KuveytTürk Bankası güvenli ödeme altyapısı üzerinden işlenmekte olup sistemimizde saklanmamaktadır.

d) Teknik veriler: IP adresi, oturum bilgileri, WhatsApp mesaj içerikleri — hizmetin sunulması ve güvenliğin sağlanması amacıyla işlenmektedir.`,
  },
  {
    baslik: '3. Kişisel Verilerin İşlenme Hukuki Dayanağı',
    metin: `KVKK madde 5 kapsamında:
— Açık rıza (madde 5/1): TC kimlik numarası dahil hassas veri işlemleri
— Sözleşmenin ifası (madde 5/2-c): Üyelik ve belge oluşturma hizmeti
— Meşru menfaat (madde 5/2-f): Hizmet güvenliği, dolandırıcılık önleme
— Kanuni yükümlülük (madde 5/2-ç): Fatura ve muhasebe kayıtları`,
  },
  {
    baslik: '4. Kişisel Verilerin Aktarıldığı Taraflar',
    metin: `Verileriniz aşağıdaki altyapı ve hizmet sağlayıcılarına aktarılabilir:
— Meta Platforms (WhatsApp Business API) — mesaj iletimi
— Railway Technologies (sunucu barındırma) — ABD merkezli, SCCs kapsamında
— Vercel Inc. (frontend barındırma) — ABD merkezli, SCCs kapsamında
— Google LLC (Gemini AI, metin analizi) — ABD merkezli, SCCs kapsamında
— KuveytTürk Bankası (ödeme işlemleri)

Verileriniz pazarlama amacıyla üçüncü taraflarla paylaşılmaz.`,
  },
  {
    baslik: '5. Veri Saklama Süreleri',
    metin: `— Üyelik bilgileri: Hesap silinene kadar + 3 yıl (ticari kayıt yükümlülüğü)
— Yer gösterme belgeleri: Oluşturma tarihinden itibaren 10 yıl (Türk Borçlar Kanunu zamanaşımı)
— Ödeme kayıtları: 10 yıl (Vergi Usul Kanunu)
— WhatsApp oturum verileri: Oturum kapanmasıyla silinir, en fazla 30 dakika
— Fotoğraflar: Belge oluşturulduktan sonra sunucudan silinir`,
  },
  {
    baslik: '6. İlgili Kişi Hakları (KVKK Madde 11)',
    metin: `Kişisel verilerinize ilişkin aşağıdaki haklara sahipsiniz:
a) Verilerinizin işlenip işlenmediğini öğrenme
b) İşlenmiş ise buna ilişkin bilgi talep etme
c) Amacını ve amacına uygun kullanılıp kullanılmadığını öğrenme
d) Yurt içi/yurt dışında aktarıldığı üçüncü kişileri bilme
e) Eksik/yanlış işlenmiş ise düzeltilmesini isteme
f) Kanuna aykırı işlenmiş ise silinmesini isteme
g) Yapılan işlemlerin aktarıldığı üçüncü kişilere bildirilmesini isteme
h) İtiraz etme ve zararın giderilmesini talep etme

Başvurularınızı yazılı olarak ${SORUMLU.adres} adresine veya ${SORUMLU.eposta} e-posta adresine iletebilirsiniz. Talebiniz 30 gün içinde sonuçlandırılır.`,
  },
  {
    baslik: '7. Veri Güvenliği',
    metin: `Kişisel verilerinizin korunması için KVKK'nın 12. maddesi kapsamında gerekli teknik ve idari tedbirler alınmaktadır:
— Tüm veri iletişimi TLS 1.2+ şifrelemesi ile korunmaktadır
— Şifreler bcrypt ile hashlenerek saklanmaktadır
— Erişim kontrolü ve yetkilendirme sistemleri uygulanmaktadır
— Güvenlik açıklarına karşı düzenli denetim yapılmaktadır`,
  },
  {
    baslik: '8. Çerezler (Cookies)',
    metin: `Sistemimiz yalnızca oturum yönetimi amacıyla zorunlu çerezler kullanmaktadır. Pazarlama veya analitik çerezi kullanılmamaktadır.`,
  },
  {
    baslik: '9. Değişiklikler',
    metin: `Bu politika gerektiğinde güncellenebilir. Önemli değişiklikler e-posta veya sistem bildirimi aracılığıyla duyurulur.`,
  },
  {
    baslik: '10. İletişim',
    metin: `KVKK ve gizlilik konularındaki tüm başvurular için:
E-posta: ${SORUMLU.eposta}
Telefon: ${SORUMLU.tel}
Adres: ${SORUMLU.adres}`,
  },
];

export default function Gizlilik() {
  return (
    <Layout>
      <div style={{ maxWidth: 720, margin: '0 auto' }}>
        <h1 style={{ fontSize: 24, fontWeight: 800, color: '#0f172a', marginBottom: 4 }}>
          KVKK Aydınlatma Metni & Gizlilik Politikası
        </h1>
        <p style={{ color: '#64748b', fontSize: 13, marginBottom: 8 }}>
          Son güncelleme: Nisan 2026
        </p>
        <div style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: 10,
                      padding: '12px 16px', marginBottom: 32, fontSize: 13, color: '#15803d' }}>
          Bu metin, 6698 sayılı Kişisel Verilerin Korunması Kanunu'nun 10. maddesi ve
          Aydınlatma Yükümlülüğünün Yerine Getirilmesinde Uyulacak Usul ve Esaslar
          Hakkında Tebliğ kapsamında hazırlanmıştır.
        </div>

        {MADDELER.map(item => (
          <div key={item.baslik} style={{ marginBottom: 28 }}>
            <h2 style={{ fontSize: 15, fontWeight: 700, color: '#1e293b', marginBottom: 10 }}>
              {item.baslik}
            </h2>
            <p style={{ fontSize: 14, color: '#475569', lineHeight: 1.8, margin: 0,
                        whiteSpace: 'pre-line' }}>
              {item.metin}
            </p>
          </div>
        ))}

        <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: 20, marginTop: 12,
                      fontSize: 12, color: '#94a3b8', textAlign: 'center' }}>
          {SORUMLU.unvan} · MERSİS: {SORUMLU.mersis}
        </div>
      </div>
    </Layout>
  );
}
