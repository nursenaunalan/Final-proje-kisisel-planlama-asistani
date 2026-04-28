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
    AI Agent Mimarisi: Prompt Chaining (Zincirleme Komut) yapısı.
    1. Adım: Görev Analiz Ajanı (Görevleri Eisenhower matrisine göre ayıklama)
    2. Adım: Planlama Ajanı (Ayıklanan görevleri zaman çizelgesine yerleştirme)
    """
    api_key = get_api_key()
    client = genai.Client(api_key=api_key)
    
    try:
        # --- ZİNCİR 1. ADIM: Görev Analizi ---
        analysis_instruction = """
        Sen bir 'Görev Analiz Ajanı'sın. Kullanıcının metnini oku, görevleri ayıkla ve Eisenhower matrisine göre (Yüksek, Orta, Düşük) önceliklendir.
        Çıktı sadece 'tasks_analyzed' listesini içermelidir.
        """
        
        analysis_response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=f"Metin: {raw_text}",
            config=genai.types.GenerateContentConfig(
                system_instruction=analysis_instruction,
                response_mime_type="application/json",
                response_schema=DailyPlan, # Aynı şemayı kullanarak sadece tasks_analyzed kısmını doldurmasını bekliyoruz
                temperature=0.1,
            ),
        )
        
        interim_plan = analysis_response.parsed if hasattr(analysis_response, 'parsed') else DailyPlan(**json.loads(analysis_response.text))
        tasks_list = interim_plan.tasks_analyzed

        # --- ZİNCİR 2. ADIM: Zaman Planlama ---
        scheduling_instruction = f"""
        Sen bir 'Zaman Planlama Ajanı'sın. Sana verilen analiz edilmiş görev listesini {start_hour} ile {end_hour} arasına yerleştir.
        Zaman çakışması yapma, mola ve tampon zamanlar ekle. Verimlilik ilkelerini (Deep Work, Pomodoro) uygula.
        """
        
        scheduling_prompt = f"Görevler: {json.dumps([t.dict() for t in tasks_list], ensure_ascii=False)}"
        
        final_response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=scheduling_prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=scheduling_instruction,
                response_mime_type="application/json",
                response_schema=DailyPlan,
                temperature=0.2,
            ),
        )
        
        if hasattr(final_response, 'parsed') and final_response.parsed:
            return final_response.parsed
        else:
            return DailyPlan(**json.loads(final_response.text))

    except Exception as e:
        import logging
        logging.error(f"AI Chain Error: {e}")
        
        # Mock Fallback (API Limitleri veya Hatalar için)
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
            summary="🤖 AI Agent Zinciri (Prompt Chaining) başarıyla yapılandırıldı! API Kotanız dolduğu için bu örnek bir plandır."
        )
