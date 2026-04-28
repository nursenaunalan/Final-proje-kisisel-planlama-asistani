from pydantic import BaseModel, Field
from typing import List

class TaskItem(BaseModel):
    task_name: str = Field(description="Görev adı veya açıklaması")
    estimated_minutes: int = Field(description="Görevin tamamlanması için tahmini süre (dakika cinsinden)")
    priority: str = Field(description="Görev önceliği (Yüksek, Orta, Düşük)")
    category: str = Field(description="Görev kategorisi (İş, Kişisel, Sağlık, Eğitim vb.)")

class ScheduledSlot(BaseModel):
    start_time: str = Field(description="Başlangıç saati (Örn: 09:00)")
    end_time: str = Field(description="Bitiş saati (Örn: 10:30)")
    task_name: str = Field(description="Görevin adı")
    details: str = Field(description="Kısa tavsiye veya not")

class DailyPlan(BaseModel):
    tasks_analyzed: List[TaskItem] = Field(description="Analiz edilen ve ayrıştırılan görevlerin listesi")
    schedule: List[ScheduledSlot] = Field(description="Zaman çizelgesine yerleştirilmiş plan")
    summary: str = Field(description="Günün genel bir özeti ve motivasyon mesajı")

class PlanRequest(BaseModel):
    raw_text: str = Field(description="Kullanıcının serbest metin olarak girdiği günlük plan")
    start_hour: str = Field(default="09:00", description="Güne başlangıç saati")
    end_hour: str = Field(default="18:00", description="Gün bitiş saati")
