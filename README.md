# XiEn CC Checker v2 – New Era

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
![Status](https://img.shields.io/badge/status-stable-green)

**XiEn CC Checker v2**, Python ile geliştirilmiş, terminal tabanlı bir kart analiz ve doğrulama aracıdır. Tool; kart format kontrolü, Luhn algoritması doğrulaması, BIN analizi, simülasyon tabanlı kontrol mekanizmaları ve detaylı loglama özelliklerini tek bir yapı altında sunar.

Bu proje **eğitim, test ve yazılım geliştirme amaçlı** olarak hazırlanmıştır. Gerçek ödeme altyapılarıyla doğrudan işlem yapmaz.

---

## ⚠️ Yasal Uyarı

Bu proje **yalnızca eğitim ve test amaçlıdır**. Gerçek kişilere veya kurumlara ait kredi/banka kartı bilgilerinin izinsiz şekilde kullanılması, denenmesi, saklanması veya paylaşılması **hukuka aykırıdır** ve ciddi yaptırımlara tabidir. Bu yazılımın yasa dışı amaçlarla kullanımından doğabilecek tüm sorumluluk **tamamen kullanıcıya aittir**.

Tool içerisinde yer alan tüm kontrol mekanizmaları ya **algoritmik doğrulama** (ör. Luhn kontrolü) ya da **simülasyon mantığı** ile çalışır. Geliştirici, bu yazılımın kullanımından doğabilecek hiçbir doğrudan veya dolaylı zarardan sorumlu tutulamaz.

---

## 🛠️ Tool Ne Yapar?

XiEn CC Checker v2, kullanıcıdan alınan kart verilerini birden fazla doğrulama katmanından geçirerek teknik bir analiz sonucu üretir. Bu doğrulamalar; kart numarasının yapısal geçerliliği, kart türü tespiti ve BIN (ilk 6 hane) analizlerini kapsar.

Tool, hem **tek kart** hem de **dosya üzerinden çoklu kart** kontrolünü destekler. Bu sayede büyük veri setleriyle çalışan geliştiriciler veya test senaryoları hazırlayan kullanıcılar için pratik bir çözüm sunar.

Ayrıca tool; **ayar dosyası**, **detaylı loglama sistemi**, **kart maskeleme**, **test modu** ve **Telegram bildirim entegrasyonu** gibi ileri seviye özelliklere sahiptir.

---

## 🎯 Hangi Amaçlarla Kullanılabilir?

Bu proje özellikle **Python öğrenenler**, **CLI (terminal) tabanlı uygulama geliştirmek isteyenler** ve **doğrulama / loglama sistemlerini incelemek isteyen geliştiriciler** için öğretici bir örnektir.

Sahte veya test amaçlı kart verileriyle çalışan sistemlerde, kart formatı ve algoritma doğrulamasını hızlıca yapmak için kullanılabilir. Gerçek finansal sistemlerle kullanılmak üzere tasarlanmamıştır.

---

## ⚙️ Kurulum

### Gereksinimler

* Python **3.8 veya üzeri**
* pip
* Windows / Linux / macOS
* İnternet bağlantısı (BIN API ve Telegram için)

### Repository’yi Klonla

```bash
git clone https://github.com/kullaniciadi/XiEn-CC-Checker-v2.git
cd XiEn-CC-Checker-v2
```

### Gerekli Kütüphaneleri Kur

```bash
pip install requests colorama pystyle
```

> `pystyle` kurulu değilse, tool ilk çalıştırmada otomatik olarak kurmayı dener.

---

## ▶️ Kullanım

### Tool’u Başlat

```bash
python "XiEn CC Checker v2 #newera.py"
```

### Giriş Anahtarı

Program açıldığında **K3y** ister:

```
XiEn
```

---

### 📌 Kart Formatı

```
KartNumarası|Ay|Yıl|CVV
```

Örnek:

```
4111111111111111|12|26|123
```

---

### 🔹 Tek Kart Check

* Kart format doğrulaması
* Luhn algoritması kontrolü
* Kart tipi tespiti (Visa, Mastercard, Troy, Amex)
* BIN analizi
* Simülasyon sonucu

📸 *Buraya tek kart check ekran görüntüsü eklenebilir*

---

### 🔹 Dosyadan Çoklu Check

* Dosyadaki her satır 1 kart olacak şekilde okunur
* Toplam, onaylanan, reddedilen ve hatalı kart sayıları gösterilir
* Satır satır detaylı çıktı verir

📸 *Buraya dosyadan check ekran görüntüsü eklenebilir*

---

### 🔹 Telegram Entegrasyonu

* Onaylanan kartlar için otomatik bildirim
* Bot Token ve Chat ID desteği
* Ayarlar `ayarlar.json` dosyasında saklanır

---

## 🧠 Teknik Detaylar

* **Luhn algoritması** ile kart doğrulama
* **BIN kontrolü** (yerel JSON + API fallback)
* **Log maskeleme sistemi** (kart numarası gizleme)
* **Test modu** (gerçek check yapılmaz)
* **Detaylı loglama** (`log.txt`)
* **Hata toleranslı yapı**
* **Renkli terminal arayüzü**

---

## ✍️ İmza

```
By. XiEn INC
XiEn CC Checker v2 – New Era
```