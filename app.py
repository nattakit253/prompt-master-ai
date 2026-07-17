import json
import time
import streamlit as st
from google import genai
from google.genai import types

# 1. ตั้งค่าหน้าจอหน้าเว็บ
st.set_page_config(
    page_title="Prompt Master AI",
    page_icon="🧙‍♂️",
    layout="wide"
)

st.title("🧙‍♂️ Prompt Master AI (Free Tier Only)")
st.write("เปลี่ยนข้อความธรรมดาของคุณ ให้กลายเป็นคำตอบระดับมืออาชีพด้วยระบบ AI Expert Router")
st.write("---")

# 2. ดึง API Key จาก Secrets
raw_api_key = None
if "GEMINI_API_KEY" in st.secrets:
    raw_api_key = st.secrets["GEMINI_API_KEY"]
else:
    raw_api_key = st.sidebar.text_input("ใส่ Google Gemini API Key สำหรับเทสบนเครื่อง:", type="password")

api_key = None
if raw_api_key:
    api_key = raw_api_key.strip().replace('"', '').replace("'", "")

user_input = st.text_area("✍️ พิมพ์สิ่งที่คุณต้องการถามหรืออยากให้ AI ช่วย (เช่น: อยากปลูกผักชีในบ้าน):")

if st.button("🚀 รันระบบแปลงร่าง AI"):
    if not api_key:
        st.warning("⚠️ ไม่พบ API Key กรุณาตั้งค่าระบบหลังบ้านก่อนใช้งาน")
    elif not user_input.strip():
        st.error("⚠️ กรุณาพิมพ์ข้อความเพื่อถาม AI")
    else:
        # รายชื่อโมเดลฟรีทั้งหมดของ Google
        models_to_try = [
            'gemini-2.5-flash', 
            'gemini-2.0-flash', 
            'gemini-1.5-flash',
            'gemini-1.5-pro'
        ]
        
        client = genai.Client(api_key=api_key)
        selected_model = None
        error_logs = []
        
        with st.spinner("🧠 กำลังค้นหาช่องทางและเชื่อมต่อสมองกล AI..."):
            for model_name in models_to_try:
                try:
                    client.models.generate_content(
                        model=model_name,
                        contents="Hi"
                    )
                    selected_model = model_name
                    break
                except Exception as e:
                    error_logs.append(f"- {model_name}: {str(e)}")
                    continue
        
        # กรณีโชคร้ายโควตาเต็มทุกตัวจริง ๆ (ชน Rate Limit 429)
        if not selected_model:
            st.error("❌ ขออภัยด้วยครับ! ขณะนี้โควตาฟรีของทุกโมเดลในบัญชีของคุณเต็มชั่วคราวเนื่องจากมีการใช้งานหนาแน่น")
            st.info("💡 ระบบกำลังทำการจำกัดเวลาคูลดาวน์เพื่อรีเซ็ตสิทธิ์ฟรีให้คุณอัตโนมัติ กรุณารอสักครู่...")
            
            # --- ⏳ ระบบนับเวลาถอยหลังและรีเฟรชออโต้ ---
            countdown_placeholder = st.empty()
            
            # ตั้งเวลานับถอยหลัง 30 วินาที (ตามที่ Google แจ้งให้ Retry)
            for seconds_left in range(30, -1, -1):
                if seconds_left > 0:
                    countdown_placeholder.metric(
                        label="⏳ ระบบจะพร้อมใช้งานและรีเฟรชหน้าเว็บใหม่ในอีก", 
                        value=f"{seconds_left} วินาที"
                    )
                    time.sleep(1)
                else:
                    countdown_placeholder.success("🔄 กำลังรีเฟรชหน้าเว็บใหม่อัตโนมัติ...")
                    time.sleep(1)
            
            # สั่งรีเฟรชหน้าเว็บอัตโนมัติ
            st.rerun()
            
        else:
            with st.spinner(f"🧙‍♂️ ใช้โมเดล {selected_model} กำลังวิเคราะห์และแปลงร่างเป็นผู้เชี่ยวชาญ..."):
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
                    
                    st.success("✨ แปลงร่างสำเร็จ!")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"🧙‍♂️ **ร่างผู้เชี่ยวชาญที่ใช้:**\n\n{persona}")
                    with col2:
                        st.warning(f"📝 **พรอมต์ที่ปรับแต่งใหม่:**\n\n{optimized_prompt}")
                    
                    st.write("---")
                    
                    with st.spinner(f"💬 กำลังส่งต่อให้ {persona} สร้างคำตอบที่ดีที่สุด..."):
                        final_response = client.models.generate_content(
                            model=selected_model,
                            contents=optimized_prompt,
                            config=types.GenerateContentConfig(
                                system_instruction=f"คุณคือผู้เชี่ยวชาญในบทบาท: {persona} จงตอบคำถามต่อไปนี้อย่างมืออาชีพ ละเอียด เป็นขั้นตอน และอ่านง่ายที่สุด"
                            )
                        )
                        
                        st.subheader("🎯 คำตอบสุดท้ายจาก AI ผู้เชี่ยวชาญ:")
                        st.markdown(final_response.text)
                        
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดระหว่างการทำงานของระบบ: {e}")
