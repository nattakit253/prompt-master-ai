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

st.title("🧙‍♂️ Prompt Master AI")
st.write("เปลี่ยนข้อความธรรมดาของคุณ ให้กลายเป็นคำตอบระดับมืออาชีพด้วยระบบ AI Expert Router")
st.write("---")

# 2. ดึง API Key จาก Secrets หลังบ้าน และขัดเกลาล้างขยะในข้อความออกให้เกลี้ยง
raw_api_key = None
if "GEMINI_API_KEY" in st.secrets:
    raw_api_key = st.secrets["GEMINI_API_KEY"]
else:
    raw_api_key = st.sidebar.text_input("ใส่ Google Gemini API Key สำหรับเทสบนเครื่อง:", type="password")

# ฟังก์ชันทำความสะอาดคีย์ (ลบเว้นวรรค, ลบเครื่องหมายคำพูดที่อาจก๊อปปี้ติดมา)
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
        # ใช้โมเดลพื้นฐานที่สุดของเวอร์ชันปัจจุบันที่มั่นใจว่ามีอยู่ชัวร์ๆ
        TARGET_MODEL = 'gemini-2.0-flash'
        
        with st.spinner("🧠 กำลังเชื่อมต่อสมองกล AI..."):
            try:
                # เรียกใช้ Client พร้อมคีย์ที่ทำความสะอาดแล้ว
                client = genai.Client(api_key=api_key)
                
                # ออกแบบการทำงานของ Router & Optimiser
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
                    model=TARGET_MODEL,
                    contents=router_prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                
                # แกะข้อมูล JSON
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
                
                # ส่งให้ผู้เชี่ยวชาญตอบจริง
                with st.spinner(f"💬 กำลังส่งต่อให้ {persona} สร้างคำตอบที่ดีที่สุด..."):
                    final_response = client.models.generate_content(
                        model=TARGET_MODEL,
                        contents=optimized_prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=f"คุณคือผู้เชี่ยวชาญในบทบาท: {persona} จงตอบคำถามต่อไปนี้อย่างมืออาชีพ ละเอียด เป็นขั้นตอน และอ่านง่ายที่สุด"
                        )
                    )
                    
                    st.subheader("🎯 คำตอบสุดท้ายจาก AI ผู้เชี่ยวชาญ:")
                    st.markdown(final_response.text)
                    
            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาดทางเทคนิค: {e}")
