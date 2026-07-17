import json
import time
import os
from datetime import datetime, timedelta
import streamlit as st
from google import genai
from google.genai import types

# 1. ตั้งค่าหน้าจอหน้าเว็บและดีไซน์ธีม
st.set_page_config(
    page_title="Prompt Master",
    page_icon="🧙‍♂️",
    layout="centered"
)

# 🎨 CSS ตกแต่งสไตล์เรียบหรู
st.markdown("""
    <style>
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(45deg, #2563EB, #7C3AED);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    .emoji-fix {
        font-family: "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif;
    }
    .subtitle {
        font-size: 1.2rem;
        text-align: center;
        color: #4B5563;
        margin-bottom: 35px;
    }
    .step-box-left {
        background-color: #EFF6FF;
        border-left: 5px solid #2563EB;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    .step-box-right {
        background-color: #F5F3FF;
        border-left: 5px solid #7C3AED;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    .answer-container {
        background-color: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 25px;
        margin-top: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .stButton>button {
        background: linear-gradient(45deg, #2563EB, #7C3AED);
        color: white;
        font-weight: bold;
        padding: 12px 24px;
        border-radius: 8px;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

# ----------------- 📦 ระบบจัดการโควตาข้อมูลจริง -----------------
DB_FILE = "quota_db.json"
MAX_QUOTA_PER_DAY = 150  

def load_quota():
    today_str = datetime.now().strftime("%Y-%m-%d")
    default_data = {"date": today_str, "used_today": 0}
    
    if not os.path.exists(DB_FILE):
        return default_data
    
    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            if data.get("date") != today_str:
                return default_data
            return data
    except Exception:
        return default_data

def save_quota(used_today):
    today_str = datetime.now().strftime("%Y-%m-%d")
    data = {"date": today_str, "used_today": used_today}
    try:
        with open(DB_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        st.error(f"ไม่สามารถอัปเดตยอดโควตาได้: {e}")

quota_data = load_quota()
used_today = quota_data["used_today"]
remaining_quota = max(0, MAX_QUOTA_PER_DAY - used_today)

# คำนวณเวลาที่สิทธิ์โควตารายวันของ Google (เวลา 07:00 น.) จะรีเซ็ตขึ้นมาใหม่
now = datetime.now()
reset_time = datetime(now.year, now.month, now.day, 7, 0, 0)
if now >= reset_time:
    reset_time += timedelta(days=1)
time_to_reset = reset_time - now
hours, remainder = divmod(time_to_reset.seconds, 3600)
minutes, _ = divmod(remainder, 60)

# ----------------- 🖥️ หน้าตาเว็บหลัก -----------------
st.markdown("<div class='main-title'><span class='emoji-fix'>🧙‍♂️</span> Prompt Master</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>แปลงข้อความธรรมดา ให้เป็นคำตอบจากผู้เชี่ยวชาญระดับมืออาชีพในพริบตา</div>", unsafe_allow_html=True)

# หลอดพลังแสดงสถานะโควตา
progress_percentage = min(1.0, used_today / MAX_QUOTA_PER_DAY)
st.progress(
    progress_percentage, 
    text=f"🔋 โควตาฟรีที่เหลือของระบบวันนี้: {remaining_quota} ครั้ง (ใช้ไปแล้ว {used_today} จากทั้งหมด {MAX_QUOTA_PER_DAY} ครั้ง)"
)

# กล่องข้อมูลแสดงเวลารีเซ็ตจริงของ Google ให้เพื่อน ๆ เห็นชัดเจน
st.info(f"📅 **ข้อมูลโควตาฟรีฝั่ง Google API:** หากระบบโดนจำกัดสิทธิ์ชั่วคราว โควตาหลักจะทำการรีเซ็ตใหม่ทั้งหมดในอีกประมาณ **{hours} ชั่วโมง {minutes} นาที** (ตอนเวลา 07:00 น. ของวันพรุ่งนี้)")

st.write("")

user_input = st.text_area(
    "✍️ พิมพ์สิ่งที่คุณต้องการถามหรือให้ช่วย (สั้น ๆ หรือคิดอะไรได้พิมพ์ใส่มาได้เลย):", 
    placeholder="ตัวอย่างเช่น: 'ปลาดุกยาวไหม' หรือ 'ช่วยคิดสโลแกนร้านกาแฟเท่ๆ'",
    height=120
)

st.write("")

if st.button("🚀 รันระบบแปลงร่าง AI และหาคำตอบ"):
    raw_api_key = st.secrets.get("GEMINI_API_KEY", "")
    api_key_clean = raw_api_key.strip().replace('"', '').replace("'", "") if raw_api_key else None
    
    if not api_key_clean:
        st.warning("⚠️ ไม่พบ API Key บนระบบหลังบ้าน กรุณาตั้งค่าความลับบนคลาวด์ก่อนใช้งานครับ")
    elif not user_input.strip():
        st.error("⚠️ กรุณาพิมพ์ข้อความอธิบายความต้องการของคุณก่อนนะครับ")
    elif remaining_quota <= 0:
        st.error(f"🚨 ขออภัยด้วยครับ! โควตาการใช้งานของวันนี้เต็มเรียบร้อยแล้ว ({MAX_QUOTA_PER_DAY}/{MAX_QUOTA_PER_DAY} ครั้ง)")
    else:
        models_to_try = ['gemini-1.5-flash', 'gemini-2.0-flash', 'gemini-2.5-flash']
        client = genai.Client(api_key=api_key_clean)
        selected_model = None
        
        with st.spinner("🧠 กำลังเชื่อมต่อเครือข่าย AI..."):
            for model_name in models_to_try:
                try:
                    client.models.generate_content(model=model_name, contents="Hi")
                    selected_model = model_name
                    break
                except Exception:
                    continue
        
        if not selected_model:
            st.error("❌ ขออภัยด้วยครับ! ขณะนี้ตัวเชื่อมต่อฟรีของโมเดลทั้งหมดเต็มชั่วคราวเนื่องจากมีการใช้งานหนาแน่น")
            st.info("💡 ระบบกำลังทำการเปิดคูลดาวน์สิทธิ์ให้อัตโนมัติ รบกวนรอสักครู่และห้ามปิดหน้าต่างนี้...")
            
            countdown_placeholder = st.empty()
            for seconds_left in range(30, -1, -1):
                if seconds_left > 0:
                    countdown_placeholder.metric(
                        label="⏳ ระบบจะพร้อมรันคำถามใหม่และรีโหลดหน้าจอในอีก", 
                        value=f"{seconds_left} วินาที"
                    )
                    time.sleep(1)
                else:
                    countdown_placeholder.success("🔄 กำลังรีเฟรชหน้าต่างใหม่อัตโนมัติ...")
                    time.sleep(1)
            st.rerun()
            
        else:
            with st.spinner("🧙‍♂️ กำลังวิเคราะห์เจตนาและเตรียมแปลงร่างเป็นผู้เชี่ยวชาญ..."):
                try:
                    router_prompt = f"""
                    คุณคือ AI ผู้เชี่ยวชาญด้าน Prompt Engineering และ Intent Classification
                    หน้าที่ของคุณคือ:
                    1. วิเคราะห์ว่าข้อความของผู้ใช้ต่อไปนี้ เกี่ยวข้องกับสาขาวิชาหรืออาชีพผู้เชี่ยวชาญด้านใดมากที่สุด
                    2. นำข้อความดิบของผู้ใช้ไปเขียนใหม่ (Prompt Expansion) ให้กลายเป็นพรอมต์ที่สมบูรณ์ มีประสิทธิภาพสูงสุด มีโครงสร้างชัดเจน
                    
                    ข้อความดิบของผู้ใช้: "{user_input}"
                    
                    ให้ตอบกลับในรูปแบบ JSON เท่านั้น ห้ามมีคำอธิบายอื่นนอกเหนือจากโครงสร้างนี้:
                    {{
                        "persona": "ระบุบทบาทผู้เชี่ยวชาญที่เหมาะสมที่สุด",
                        "optimized_prompt": "เขียนพรอมต์ใหม่ที่ขยายความและสมบูรณ์แบบที่สุด"
                    }}
                    """
                    
                    response = client.models.generate_content(
                        model=selected_model,
                        contents=router_prompt,
                        config=types.GenerateContentConfig(response_mime_type="application/json")
                    )
                    
                    result = json.loads(response.text)
                    persona = result.get("persona")
                    optimized_prompt = result.get("optimized_prompt")
                    
                    st.write("---")
                    st.markdown("### ⚙️ ขั้นตอนการประมวลผลเบื้องหลัง (Behind the Scenes)")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"""
                            <div class='step-box-left'>
                                <h4 style='color: #1E40AF; margin-top: 0;'>🧙‍♂️ AI แปลงร่างเป็น:</h4>
                                <p style='font-size: 1.1rem; font-weight: bold; color: #1E3A8A; margin: 0;'>{persona}</p>
                            </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                            <div class='step-box-right'>
                                <h4 style='color: #5B21B6; margin-top: 0;'>📝 เรียบเรียงพรอมต์ใหม่ให้เสร็จสิ้น:</h4>
                                <p style='font-size: 0.95rem; color: #4C1D95; margin: 0; font-style: italic;'>"{optimized_prompt}"</p>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.write("")
                    
                    with st.spinner(f"💬 กำลังส่งต่อให้ {persona} จัดทำคำตอบระดับมืออาชีพ..."):
                        final_response = client.models.generate_content(
                            model=selected_model,
                            contents=optimized_prompt,
                            config=types.GenerateContentConfig(
                                system_instruction=f"คุณคือผู้เชี่ยวชาญในบทบาท: {persona} จงตอบคำถามต่อไปนี้อย่างมืออาชีพ ละเอียด เป็นขั้นตอน และอ่านง่ายที่สุด"
                            )
                        )
                        
                        st.markdown("<div class='answer-container'>", unsafe_allow_html=True)
                        st.subheader(f"🎯 คำตอบสุดท้ายจาก {persona}:")
                        st.markdown(final_response.text)
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        save_quota(used_today + 1)
                        
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการประมวลผลระบบ: {e}")
