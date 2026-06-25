import streamlit as st
from rembg import remove
from PIL import Image
import io
import zipfile
from datetime import datetime

st.set_page_config(page_title="西垣の切り抜き部屋", page_icon="✂️")

st.title("✂️ 西垣の切り抜き部屋")
st.write("最大5枚まで一括処理できます")

# ファイルアップロード（5枚まで）
files = st.file_uploader(
    "画像を選んでね",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if files:
    # 5枚に制限
    if len(files) > 5:
        st.warning("5枚までだよ！")
        files = files[:5]
    
    st.write(f"✅ {len(files)}枚 選択中")
    
    # 処理ボタン
    if st.button("切り抜く！"):
        results = []
        
        for i, f in enumerate(files):
            with st.spinner(f"{i+1}/{len(files)}枚目 処理中..."):
                # 切り抜き
                out = remove(f.getvalue())
                img = Image.open(io.BytesIO(out))
                results.append(img)
        
        st.success("完了！ 🎉")
        st.balloons()
        
        # 結果を表示
        for i, img in enumerate(results):
            st.image(img, caption=files[i].name, use_container_width=True)
            
            # ダウンロード
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            st.download_button(
                f"⬇️ {files[i].name}",
                buf.getvalue(),
                file_name=f"切り抜き_{i}.png",
                mime="image/png"
            )
        
        # ZIPで一括ダウンロード
        if len(results) > 1:
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, 'w') as zf:
                for i, img in enumerate(results):
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    zf.writestr(f"切り抜き_{i}.png", buf.getvalue())
            
            zip_buf.seek(0)
            st.download_button(
                "📦 全部まとめてZIP",
                zip_buf.getvalue(),
                file_name=f"切り抜き_{datetime.now().strftime('%H%M')}.zip",
                mime="application/zip"
            )
