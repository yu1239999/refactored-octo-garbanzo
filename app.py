import streamlit as st
import io
from PIL import Image
from rembg import remove

st.set_page_config(page_title="テスト", page_icon="🧪")
st.title("🧪 背景除去テスト（1枚）")

uploaded_file = st.file_uploader("画像を1枚アップロード", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="元の画像", use_container_width=True)
    
    if st.button("実行"):
        with st.spinner("処理中..."):
            try:
                result_bytes = remove(uploaded_file.getvalue())
                result = Image.open(io.BytesIO(result_bytes))
                st.image(result, caption="結果", use_container_width=True)
                
                buf = io.BytesIO()
                result.save(buf, format="PNG")
                buf.seek(0)
                st.download_button("ダウンロード", buf.getvalue(), file_name="result.png", mime="image/png")
            except Exception as e:
                st.error(f"エラー: {e}")
