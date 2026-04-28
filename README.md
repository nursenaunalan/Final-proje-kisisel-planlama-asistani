# AI Agent Tabanlı Kişisel Planlama Asistanı

Bu proje, günlük karmaşık görevlerinizi analiz edip otomatik bir şekilde planlayan ve önceliklendiren bir yapay zeka asistanıdır. Google GenAI (Gemini) modellerini kullanarak görevlerinizi Eisenhower Matrisi mantığıyla sıralar.

## Proje Yapısı

- **`backend/`**: FastAPI uygulaması ve AI Agent mantığı (Prompt zinciri ve veri modelleri).
- **`frontend/`**: Streamlit tabanlı modern ve şık kullanıcı arayüzü.

## Kurulum ve Çalıştırma

1. **Bağımlılıkları Yükleyin**
   ```bash
   pip install -r requirements.txt
   ```

2. **API Anahtarını Ayarlayın**
   - Proje dizinindeki `.env.example` dosyasının adını `.env` olarak değiştirin.
   - İçerisine Google Gemini API anahtarınızı yapıştırın.
   ```
   GEMINI_API_KEY=sizin_api_anahtariniz_buraya
   ```

3. **Backend Sunucusunu Başlatın** (Terminal 1)
   ```bash
   # Ana proje dizininde çalıştırın:
   uvicorn backend.main:app --reload
   ```
   *FastAPI sunucusu `http://localhost:8000` adresinde başlayacaktır.*

4. **Arayüzü Başlatın** (Terminal 2)
   ```bash
   # Ana proje dizininde çalıştırın:
   streamlit run frontend/app.py
   ```
   *Streamlit uygulaması tarayıcınızda otomatik olarak açılacaktır.*

## Canlıya Alma (Deployment)

Projede iki ayrı sunucu yapısı (FastAPI ve Streamlit) zorunlu kılındığı için canlıya alırken iki aşamalı bir yol izlemelisiniz:

### Aşama 1: FastAPI Backend'in Canlıya Alınması (Örn: Render.com)
1. GitHub deponuzu [Render.com](https://render.com)'a bağlayın ve yeni bir **Web Service** oluşturun.
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. Environment Variables kısmına `GEMINI_API_KEY` değerinizi ekleyin.
5. Deploy edin ve size verilen URL'i (örn: `https://benim-backendim.onrender.com`) kopyalayın.

### Aşama 2: Streamlit Frontend'in Canlıya Alınması (Streamlit Cloud)
1. [Streamlit Community Cloud](https://share.streamlit.io/)'a girin ve deponuzu seçin.
2. Main file path kısmına: `frontend/app.py` yazın.
3. Deploy etmeden önce **Advanced Settings -> Secrets** alanına girin ve aşağıdaki ayarı ekleyin:
   ```toml
   API_URL = "https://benim-backendim.onrender.com/generate-plan"
   ```
   *(Buradaki URL'yi 1. Aşamadan aldığınız kendi Backend URL'niz ile değiştirin ve sonuna `/generate-plan` eklemeyi unutmayın)*
4. Deploy butonuna basın! Uygulamanız tamamen canlıda olacaktır.
