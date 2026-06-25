import streamlit as st
import io
from PIL import Image
import zipfile
from datetime import datetime
from rembg import remove, new_session

st.set_page_config(page_title="西垣の切り抜き部屋", page_icon="✂️")

st.title("✂️ 西垣の切り抜き部屋")
st.write("最大5枚まで一括処理できます（人物専用モデル使用）")

@st.cache_resource
def get_session():
    # 人物専用モデルに変更！
    return new_session("u2net_human_seg")

uploaded_files = st.file_uploader(
    "画像を選んでね",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if uploaded_files:
    if len(uploaded_files) > 5:
        st.warning("5枚までだよ！")
        uploaded_files = uploaded_files[:5]
    
    st.write(f"{len(uploaded_files)}枚 選択中")
    
    if st.button("切り抜く！"):
        results = []
        progress = st.progress(0)
        status = st.empty()
        session = get_session()
        
        for i, f in enumerate(uploaded_files):
            status.info(f"{i+1}/{len(uploaded_files)}枚目 処理中...")
            try:
                output_bytes = remove(f.getvalue(), session=session)
                img = Image.open(io.BytesIO(output_bytes))
                results.append(img)
            except Exception as e:
                st.error(f"{f.name} でエラー: {e}")
            progress.progress((i + 1) / len(uploaded_files))
        
        status.empty()
        st.success("完了！ 🎉")
        st.balloons()
        
        for i, img in enumerate(results):
            st.image(img, caption=uploaded_files[i].name, use_container_width=True)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            st.download_button(
                f"⬇️ {uploaded_files[i].name}",
                buf.getvalue(),
                file_name=f"切り抜き_{i}.png",
                mime="image/png"
            )
        
        if len(results) >= 2:
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, 'w') as zf:
                for i, img in enumerate(results):
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    zf.writestr(f"切り抜き_{i}.png", buf.getvalue())
            zip_buf.seek(0)
            st.download_button(
                "📦 ZIPで一括ダウンロード",
                zip_buf.getvalue(),
                file_name=f"切り抜き_{datetime.now().strftime('%H%M')}.zip",
                mime="application/zip"
            )
