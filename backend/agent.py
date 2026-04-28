import os
import json
from google import genai
from .schemas import DailyPlan
from dotenv import load_dotenv

load_dotenv()

def get_api_key():
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return api_key
    try:
        import streamlit as st
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    raise ValueError("GEMINI_API_KEY ortam değişkeni bulunamadı. Lütfen .env veya Streamlit secrets (st.secrets) kontrol edin.")


def generate_daily_plan(raw_text: str, start_hour: str, end_hour: str) -> DailyPlan:
    """
    Google GenAI SDK kullanarak günlük planlama yapar.
    Yapılandırılmış çıktı (Structured Output) ile doğrudan Pydantic modeli döndürür.
    """
    api_key = get_api_key()
    client = genai.Client(api_key=api_key)
    
    system_instruction = f"""
Sen profesyonel bir kişisel planlama asistanısın (AI Agent). 
Görevleri Eisenhower Matrisi prensiplerine göre analiz eder, önceliklendirir ve mantıklı bir zaman çizelgesine oturtursun.
Kullanıcının girdiği serbest metin formatındaki günlük hedefleri ayrıştır.

KURALLAR:
1. Günü kesinlikle {start_hour} ile {end_hour} arasına planla ve zaman çakışması yapma.
2. VERİMLİLİK İLKELERİ: 
   - Derin Odaklanma (Deep Work): Yüksek öncelikli ve zihinsel efor gerektiren işleri sabah veya günün en verimli saatlerine (öğleden önce) yerleştir.
   - Pomodoro Tekniği: 60 dakikayı aşan görevleri 50 dk çalışma + 10 dk mola veya 25 dk çalışma + 5 dk mola şeklinde parçalara böl (Timeboxing).
   - Batching (Gruplama): E-posta, telefon, idari işler gibi birbirine benzeyen düşük odak gerektiren görevleri peş peşe (aynı zaman bloğunda) planla.
   - Tampon Zamanlar (Buffer Time): Farklı bağlamdaki iki büyük görev arasına mutlaka 10-15 dakikalık "Tampon Zaman" veya kısa molalar ekle ki zihinsel geçiş (context switching) yorgunluk yaratmasın.
3. İHTİYAÇLAR: Öğle yemeği (tercihen 12:00-13:30 arası), dinlenme ve göz yorgunluğunu önleme molalarını uygun aralıklara dağıt. Kullanıcı belirtmese de temel insani ihtiyaçları (yemek, dinlenme) plana dahil et.
4. Çıktı kesinlikle DailyPlan şemasına uygun olmalıdır.
5. Görevlerin önceliğini (Yüksek, Orta, Düşük) Eisenhower matrisine göre belirle.
6. Planın sonunda gün için kısa, verimlilik ve zaman yönetimi odaklı motive edici bir Türkçe özet/tavsiye yaz.
"""
    
    prompt = f"İşte bugünkü planım/hedeflerim: {raw_text}"
    
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=DailyPlan,
                temperature=0.2,
            ),
        )
        
        if hasattr(response, 'parsed') and response.parsed:
            return response.parsed
        else:
            # Fallback if parsed is not directly available
            data = json.loads(response.text)
            return DailyPlan(**data)
    except Exception as e:
        import logging
        logging.error(f"Gemini API Error: {e}")
        
        # Return a mock plan so the user can see the UI presentation despite API limits
        from .schemas import TaskItem, ScheduledSlot
        return DailyPlan(
            tasks_analyzed=[
                TaskItem(task_name="Örnek: Veritabanı Optimizasyonu", estimated_minutes=120, priority="Yüksek", category="İş"),
                TaskItem(task_name="Örnek: Takım Toplantısı", estimated_minutes=60, priority="Orta", category="İş"),
                TaskItem(task_name="Örnek: Yürüyüş", estimated_minutes=60, priority="Düşük", category="Sağlık")
            ],
            schedule=[
                ScheduledSlot(start_time=start_hour, end_time="11:00", task_name="Örnek: Veritabanı Optimizasyonu", details="Derin odaklanma gerektirir."),
                ScheduledSlot(start_time="11:00", end_time="12:00", task_name="Örnek: Yürüyüş", details="Zihninizi dinlendirin."),
                ScheduledSlot(start_time="14:00", end_time="15:00", task_name="Örnek: Takım Toplantısı", details="Toplantıya hazırlıklı katılın.")
            ],
            summary="🤖 DİKKAT: Gemini API kotanız dolduğu için bu örnek bir plandır. UI sunumunu görebilmeniz için simüle edilmiştir!"
        )
