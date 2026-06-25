import streamlit as st
import io
from PIL import Image

st.set_page_config(page_title="西垣の切り抜き部屋", page_icon="✂️")

st.title("✂️ 西垣の切り抜き部屋")
st.write("アップロードした画像の背景を切り抜きます。")

uploaded_file = st.file_uploader("画像をアップロード", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="元の画像", use_container_width=True)
    
    try:
        from rembg import remove
        
        with st.spinner("切り抜き中..."):
            input_bytes = uploaded_file.getvalue()
            result_bytes = remove(input_bytes)
            result = Image.open(io.BytesIO(result_bytes))
        
        st.image(result, caption="切り抜き後", use_container_width=True)
        
        buf = io.BytesIO()
        result.save(buf, format="PNG")
        buf.seek(0)
        
        st.download_button(
            label="ダウンロード",
            data=buf.getvalue(),
            file_name="removed_bg.png",
            mime="image/png"
        )
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
""", unsafe_allow_html=True)
