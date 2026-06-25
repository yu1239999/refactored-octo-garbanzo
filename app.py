import streamlit as st
from rembg import remove
from PIL import Image
import io
import zipfile
from datetime import datetime

st.set_page_config(page_title="西垣の切り抜き部屋", page_icon="✂️")

st.title("✂️ 西垣の切り抜き部屋")
st.write("画像を選んで「切り抜く！」を押すだけ")

# 1枚ずつアップロード（複数回できるようにする）
uploaded_files = st.file_uploader(
    "画像を選んでね（1枚ずつ複数回アップロードできます）",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True  # ← これで複数選択できる！
)

if uploaded_files:
    # 5枚に制限
    if len(uploaded_files) > 5:
        st.warning("5枚までだよ！最初の5枚を処理するね")
        uploaded_files = uploaded_files[:5]
    
    st.write(f"📸 {len(uploaded_files)}枚の画像を処理します")
    
    # プレビュー表示
    for i, f in enumerate(uploaded_files):
        img = Image.open(f)
        st.image(img, caption=f"{i+1}: {f.name}", width=150)
    
    if st.button("✂️ 切り抜く！"):
        results = []
        progress = st.progress(0)
        status = st.empty()
        
        for i, f in enumerate(uploaded_files):
            status.info(f"{i+1}/{len(uploaded_files)}枚目 処理中...")
            
            # 切り抜き
            out = remove(f.getvalue())
            img = Image.open(io.BytesIO(out))
            results.append(img)
            
            progress.progress((i + 1) / len(uploaded_files))
        
        status.empty()
        st.success("✅ 全部切り抜けたよ！ 🎉")
        st.balloons()
        
        # 結果表示
        for i, img in enumerate(results):
            col1, col2 = st.columns(2)
            with col1:
                st.image(img, caption=uploaded_files[i].name, use_container_width=True)
            with col2:
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                buf.seek(0)
                st.download_button(
                    f"⬇️ ダウンロード {i+1}",
                    buf.getvalue(),
                    file_name=f"切り抜き_{i}.png",
                    mime="image/png"
                )
        
        # ZIPダウンロード（2枚以上の場合）
        if len(results) >= 2:
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, 'w') as zf:
                for i, img in enumerate(results):
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    zf.writestr(f"切り抜き_{i}.png", buf.getvalue())
            
            zip_buf.seek(0)
            st.download_button(
                "📦 ZIPでまとめてダウンロード",
                zip_buf.getvalue(),
                file_name=f"切り抜き_{datetime.now().strftime('%H%M')}.zip",
                mime="application/zip"
            )
