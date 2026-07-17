import json
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

# 2. ดึง API Key
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
        # รวมรายชื่อโมเดลฟรีทั้งหมดของ Google เพื่อสลับใช้กรณีตัวใดตัวหนึ่งโควตาเต็ม (Rate Limit 429)
        # ไล่จากตัวแรงสุดใหม่ล่าสุด ไปจนถึงตัวเสถียรรุ่นก่อนหน้า
        models_to_try = [
            'gemini-2.5-flash', 
            'gemini-2.0-flash', 
            'gemini-1.5-flash',
            'gemini-1.5-pro'      # ตัวฉลาดพิเศษ (อาจจะช้ากว่าแต่เอาไว้สำรองยามคับขันได้ดี)
        ]
        
        client = genai.Client(api_key=api_key)
        
        selected_model = None
        error_logs = []
        
        with st.spinner("🧠 กำลังค้นหาช่องทางและเชื่อมต่อสมองกล AI..."):
            for model_name in models_to_try:
                try:
                    # ทดสอบยิงเชื่อมต่อด้วยคำง่าย ๆ เพื่อเช็กว่าโมเดลนี้ว่างและพร้อมทำงานหรือไม่
                    client.models.generate_content(
                        model=model_name,
                        contents="Hi"
                    )
                    selected_model = model_name
                    break  # เจอโมเดลที่ใช้งานได้แล้ว ให้หยุดลูปและเลือกใช้ตัวนี้ทันที!
                except Exception as e:
                    # เก็บ Log ข้อผิดพลาดไว้ดูหากทุกตัวใช้ไม่ได้จริง ๆ
                    error_logs.append(f"- {model_name}: {str(e)}")
                    continue
        
        # กรณีโชคร้ายโควตาเต็มทุกตัวจริง ๆ (เช่น มีคนระดมกดพร้อมกันจำนวนมากในนาทีนั้น)
        if not selected_model:
            st.error("❌ ขออภัยด้วยครับ! ขณะนี้โควตาฟรีของทุกโมเดลในบัญชีของคุณเต็มชั่วคราว")
            st.info("💡 **แนะนำสำหรับคุณ Bank และเพื่อน ๆ:** เนื่องจากใช้สิทธิ์ฟรี (Free Tier) รบกวนเว้นระยะเวลา 1-2 นาที แล้วลองกดใหม่อีกครั้งนะครับ ระบบจะรีเซ็ตโควตาให้ใหม่โดยอัตโนมัติครับ")
            with st.expander("🔍 ดูรายละเอียดข้อผิดพลาดทางเทคนิค"):
                for log in error_logs:
                    st.write(log)
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
