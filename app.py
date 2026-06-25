import streamlit as st
import io
from PIL import Image
from rembg import remove

st.set_page_config(page_title="西垣の切り抜き部屋", page_icon="✂️")

st.title("✂️ 西垣の切り抜き部屋")
st.write("画像1枚を切り抜きます。")

uploaded_file = st.file_uploader(
    "画像をアップロード",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    try:
        # 画像を開く
        img = Image.open(uploaded_file)
        
        # 小さくリサイズ（メモリ節約）
        max_size = 600
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        st.image(img, caption="元の画像", use_container_width=True)
        
        if st.button("✂️ 切り抜く！"):
            with st.spinner("処理中..."):
                # 背景切り抜き
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                buf.seek(0)
                
                output = remove(buf.getvalue())
                result = Image.open(io.BytesIO(output))
                
                st.image(result, caption="切り抜き後", use_container_width=True)
                
                # ダウンロード
                out_buf = io.BytesIO()
                result.save(out_buf, format="PNG")
                out_buf.seek(0)
                
                st.download_button(
                    "⬇️ ダウンロード",
                    out_buf.getvalue(),
                    file_name="切り抜き.png",
                    mime="image/png"
                )
    except Exception as e:
        st.error(f"エラー: {e}")
