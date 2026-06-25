import streamlit as st
import requests
import io
from PIL import Image

API_URL = "https://api-inference.huggingface.co/models/briaai/RMBG-1.4"
API_TOKEN = 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
headers = {"Authorization": f"Bearer {API_TOKEN}"}

st.set_page_config(page_title="西垣の切り抜き部屋", page_icon="✂️")
st.title("✂️ 西垣の切り抜き部屋")
st.write("画像をアップロードするだけで背景を切り抜きます。")

uploaded_file = st.file_uploader("📁 画像をアップロード", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("元の画像")
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)

    with st.spinner("✂️ 切り抜き中..."):
        input_bytes = uploaded_file.getvalue()
        response = requests.post(API_URL, headers=headers, data=input_bytes)
        result = Image.open(io.BytesIO(response.content))

    with col2:
        st.subheader("切り抜き後")
        st.image(result, use_container_width=True)

    st.success("✅ 切り抜き完了！")

    buf = io.BytesIO()
    result.save(buf, format="PNG")
    buf.seek(0)

    st.download_button(
        label="⬇️ ダウンロード",
        data=buf.getvalue(),
        file_name="removed_bg.png",
        mime="image/png",
        use_container_width=True
    )
