import streamlit as st
from PIL import Image
import torch
import os

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="AI วิเคราะห์แมลง", page_icon="🪲")
st.title("🪲 วิเคราะห์แมลงด้วย AI")
st.write("อัปโหลดภาพเพื่อดูชนิดของแมลง พร้อมคำแนะนำการจัดการ")

# ลบ cache เก่าแบบ Windows-safe
torch_hub_cache = os.path.expanduser(r"~\.cache\torch\hub")
if os.path.exists(torch_hub_cache):
    import shutil
    shutil.rmtree(torch_hub_cache)

# โหลดโมเดล YOLOv5 แบบ force reload
@st.cache_resource
def load_model():
    model = torch.hub.load(
        'ultralytics/yolov5',  # repo
        'custom',
        path=os.path.join(os.getcwd(), 'best.pt'),  # path แบบ Windows-safe
        force_reload=True
    )
    return model

try:
    model = load_model()
except Exception as e:
    st.error(f"❌ ไม่สามารถโหลดโมเดลได้: {e}")
    st.stop()
# อัปโหลดภาพ
uploaded_file = st.file_uploader("📸 เลือกภาพแมลง", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="ภาพที่อัปโหลด", use_column_width=True)

    st.write("⏳ กำลังวิเคราะห์...")
    results = model(image)

    # แสดงผลตรวจจับ
    result_img = results.render()[0]
    st.image(result_img, caption="ผลการตรวจจับ", use_column_width=True)

    labels = results.pandas().xyxy[0]['name'].tolist()
    st.write("**แมลงที่ตรวจพบ:**", ", ".join(labels))

    # กลุ่มแมลงดี / ศัตรูพืช
    beneficial = {
        'orange ladybird': '🟢 แมลงเต่าทอง - กินเพลี้ย เป็นแมลงดี ควรอนุรักษ์ไว้'
    }

    harmful = {
        'water beetle': '🔴 ด้วงน้ำ - กัดกินพืชน้ำ ใช้กับดักแสงไฟหรือเก็บออก',
        'rice borer': '🔴 หนอนเจาะลำต้นข้าว - ใช้แตนเบียนหรือกับดักแสงไฟควบคุม',
        'moth': '🔴 ผีเสื้อกลางคืน - ตัวหนอนกัดใบ ใช้เชื้อบีที (Bt)',
        'goldfly': '🔴 แมลงวันทอง - เจาะผลไม้ ใช้กับดักฟีโรโมนและเก็บผลสุกทิ้ง',
        'fruit fly': '🔴 แมลงวันผลไม้ - ทำให้ผลไม้เน่าเสีย ห่อผลหรือใช้กับดักล่อ',
        'bph': '🔴 เพลี้ยกระโดดสีน้ำตาล - ดูดน้ำเลี้ยงข้าว ใช้เชื้อราบิวเวอเรีย',
        'black beetle': '🔴 ด้วงดำ - กัดรากข้าวโพด ใช้เหยื่อล่อและพรวนดิน'
    }

    found_good, found_bad, found_unknown = [], [], []

    for label in labels:
        if label in beneficial:
            found_good.append(label)
            st.success(beneficial[label])
        elif label in harmful:
            found_bad.append(label)
            st.error(harmful[label])
        else:
            found_unknown.append(label)
            st.info(f"❓ ไม่ทราบชนิด: {label}")

    st.markdown("---")
    st.subheader("📊 สรุปผลรวม")
    st.write(f"✅ แมลงดี: {', '.join(found_good) if found_good else 'ไม่มี'}")
    st.write(f"⚠️ ศัตรูพืช: {', '.join(found_bad) if found_bad else 'ไม่มี'}")
    st.write(f"❓ ไม่ทราบชนิด: {', '.join(found_unknown) if found_unknown else 'ไม่มี'}")

    # วิเคราะห์สถานการณ์
    if len(found_bad) > len(found_good):
        st.warning("💡 พบศัตรูพืชมากกว่าแมลงดี — แนะนำใช้วิธีควบคุมแบบชีวภาพหรือติดตั้งกับดักฟีโรโมน")
    elif len(found_good) > len(found_bad):
        st.success("🌿 ระบบนิเวศดี มีแมลงดีมากกว่า ควรรักษาสมดุลไว้")
    else:
        st.info("⚖️ สมดุลแมลงดีและศัตรูพืชค่อนข้างเท่ากัน")