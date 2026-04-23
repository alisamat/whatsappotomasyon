import React from 'react';
import Layout from './Layout';

export default function Gizlilik() {
  return (
    <Layout>
      <div style={{ maxWidth: 720, margin: '0 auto' }}>
        <h1 style={{ fontSize: 24, fontWeight: 800, color: '#0f172a', marginBottom: 8 }}>Gizlilik Politikası</h1>
        <p style={{ color: '#64748b', fontSize: 13, marginBottom: 32 }}>Son güncelleme: Nisan 2026</p>

        {[
          {
            baslik: '1. Toplanan Veriler',
            metin: 'WhatsApp Otomasyon olarak; ad soyad, e-posta adresi, telefon numarası ve WhatsApp üzerinden gönderilen fotoğraf, konum ve iletişim bilgilerini toplarız. Bu veriler yalnızca hizmetimizi sunmak amacıyla kullanılır.'
          },
          {
            baslik: '2. Verilerin Kullanımı',
            metin: 'Topladığımız veriler; belge üretimi, kredi yönetimi ve müşteri iletişimi amacıyla kullanılır. Verileriniz üçüncü taraflarla pazarlama amacıyla paylaşılmaz.'
          },
          {
            baslik: '3. WhatsApp Mesajları',
            metin: 'WhatsApp üzerinden gönderilen fotoğraf, konum ve kişi bilgileri, talep ettiğiniz belgeyi oluşturmak için işlenir ve işlem tamamlandıktan sonra saklanmaz.'
          },
          {
            baslik: '4. Veri Güvenliği',
            metin: 'Verileriniz SSL/TLS şifrelemesi ile korunmaktadır. Railway ve Vercel altyapısı üzerinde barındırılmaktadır. Yetkisiz erişime karşı gerekli teknik önlemler alınmıştır.'
          },
          {
            baslik: '5. Veri Saklama',
            metin: 'Hesap bilgileriniz hesabınız aktif olduğu sürece saklanır. Hesap silme talebinde bulunmanız halinde verileriniz 30 gün içinde silinir.'
          },
          {
            baslik: '6. Haklarınız',
            metin: 'KVKK kapsamında verilerinize erişim, düzeltme, silme ve taşıma haklarına sahipsiniz. Talepleriniz için promisyazilim@gmail.com adresine başvurabilirsiniz.'
          },
          {
            baslik: '7. İletişim',
            metin: 'Gizlilik politikamız hakkında sorularınız için: promisyazilim@gmail.com'
          },
        ].map(item => (
          <div key={item.baslik} style={{ marginBottom: 24 }}>
            <h2 style={{ fontSize: 16, fontWeight: 700, color: '#1e293b', marginBottom: 8 }}>{item.baslik}</h2>
            <p style={{ fontSize: 14, color: '#475569', lineHeight: 1.7, margin: 0 }}>{item.metin}</p>
          </div>
        ))}
      </div>
    </Layout>
  );
}
