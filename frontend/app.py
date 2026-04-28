import streamlit as st
import requests
import os
import datetime

# API URL - Canlı ortamda os.environ'dan alınabilir, lokalde localhost kullanır
API_URL = os.getenv("API_URL", "http://localhost:8000/generate-plan")

# Page config
st.set_page_config(page_title="AI Planlama Asistanı", page_icon="🤖", layout="wide")

# Load CSS
def local_css():
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    else:
        st.warning(f"CSS dosyası bulunamadı: {css_path}")

local_css()

st.markdown("<h1 class='main-header'>AI Planlama Asistanı 🤖</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Karmaşık gününüzü yapay zeka ile organize edin, önceliklendirin ve yönetin.</p>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Ayarlar")
    # Using datetime module to create default times
    default_start = datetime.time(9, 0)
    default_end = datetime.time(18, 0)
    
    start_hour = st.time_input("Mesai Başlangıç", value=default_start, key="start_hour")
    end_hour = st.time_input("Mesai Bitiş", value=default_end, key="end_hour")
    st.markdown("---")
    st.markdown("**Nasıl Çalışır?**\n\nAI, hedeflerinizi Eisenhower matrisine göre değerlendirir ve mantıklı bir zaman çizelgesine yerleştirir.")

# Format times to strings
start_str = start_hour.strftime("%H:%M")
end_str = end_hour.strftime("%H:%M")

st.markdown("### 📝 Bugün Neler Yapacaksın?")
raw_text = st.text_area("Hedeflerini ve görevlerini yaz (Örn: Öğleden sonra 2 saat kod yazacağım, 14:00'da ekip toplantısı var, akşamüstü markete gidilecek...)", height=150)

if st.button("🚀 Planımı Oluştur"):
    if not raw_text.strip():
        st.warning("Lütfen planlanacak görevlerinizi girin.")
    else:
        with st.spinner("Yapay Zeka planınızı oluşturuyor... Lütfen bekleyin."):
            payload = {
                "raw_text": raw_text,
                "start_hour": start_str,
                "end_hour": end_str
            }
            
            plan_data = None
            is_fallback = False
            
            try:
                # Önce FastAPI backend'e bağlanmayı dene
                response = requests.post(API_URL, json=payload, timeout=5)
                if response.status_code == 200:
                    plan_data = response.json()
                else:
                    try:
                        error_data = response.json()
                        error_detail = error_data.get("detail", response.text)
                    except Exception:
                        error_detail = response.text
                        
                    if "429" in str(error_detail) or "RESOURCE_EXHAUSTED" in str(error_detail):
                        st.error("⚠️ Google Gemini API günlük veya anlık kullanım limitine ulaştı. Lütfen daha sonra tekrar deneyin veya .env dosyanızdaki API anahtarını değiştirin.")
                    else:
                        st.error(f"Sunucu hatası: {error_detail}")
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                # Backend çalışmıyorsa (Streamlit Cloud gibi), doğrudan agent fonksiyonunu çağır (Hybrid Fallback)
                try:
                    from backend.agent import generate_daily_plan
                    plan = generate_daily_plan(
                        raw_text=raw_text,
                        start_hour=start_str,
                        end_hour=end_str
                    )
                    plan_data = plan.dict()
                    is_fallback = True
                except Exception as e:
                    st.error(f"API'ye bağlanılamadı ve iç mekanizma başlatılamadı: {e}")
            except Exception as e:
                st.error(f"Beklenmeyen bir hata oluştu: {e}")

            # Eğer veri geldiyse (API'den veya Fallback'ten) ekrana bas
            if plan_data:
                if is_fallback:
                    st.info("ℹ️ Canlı Backend sunucusuna erişilemedi, işlem uygulama içindeki yedek sistem (Internal Agent) ile tamamlandı.")
                
                st.success("Plan başarıyla oluşturuldu!")
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown("### 🎯 Analiz Edilen Görevler")
                    for task in plan_data.get("tasks_analyzed", []):
                        priority = task.get("priority", "Orta")
                        p_class = "task-high" if "yüksek" in priority.lower() else "task-medium" if "orta" in priority.lower() else "task-low"
                        st.markdown(f"""
                        <div class='glass-card {p_class}'>
                            <h4>{task.get('task_name')}</h4>
                            <p>⏱️ {task.get('estimated_minutes')} dk | 🏷️ {task.get('category')}</p>
                            <p><strong>Öncelik:</strong> {priority}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                with col2:
                    st.markdown("### ⏳ Zaman Çizelgesi")
                    st.markdown("<div class='timeline'>", unsafe_allow_html=True)
                    for slot in plan_data.get("schedule", []):
                        st.markdown(f"""
                        <div class='timeline-item'>
                            <div class='glass-card'>
                                <span class='time-badge'>{slot.get('start_time')} - {slot.get('end_time')}</span>
                                <h4>{slot.get('task_name')}</h4>
                                <p style='color: #94a3b8; font-size: 0.9rem;'>{slot.get('details')}</p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                st.markdown("---")
                st.markdown(f"### 💡 AI Tavsiyesi\n> {plan_data.get('summary')}")
