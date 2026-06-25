import streamlit as st
import io
from PIL import Image, ImageEnhance
import zipfile
from datetime import datetime
from rembg import remove, new_session

st.set_page_config(page_title="商品切り抜き部屋", page_icon="📦")

st.title("📦 商品切り抜き部屋")
st.write("白い商品もキレイに切り抜きます")

@st.cache_resource
def get_session():
    return new_session("u2net")

uploaded_files = st.file_uploader(
    "商品画像を選んでね",
    type=["jpg", "jpeg", "png", "webp"],  # ← webpも追加
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
                # ===== エラー対策：画像を確実に開く =====
                try:
                    img = Image.open(f)
                    # RGB変換（念のため）
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                except Exception as e:
                    st.error(f"⚠️ {f.name} が開けません（ファイルが壊れてるかも）")
                    continue
                
                # コントラスト調整
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.2)
                
                # バイナリに変換
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                buf.seek(0)
                
                # 背景切り抜き
                output_bytes = remove(buf.getvalue(), session=session)
                result_img = Image.open(io.BytesIO(output_bytes))
                results.append(result_img)
                
            except Exception as e:
                st.error(f"{f.name} でエラー: {e}")
            
            progress.progress((i + 1) / len(uploaded_files))
        
        status.empty()
        
        if results:
            st.success(f"✅ {len(results)}枚処理完了！ 🎉")
            st.balloons()
            
            for i, img in enumerate(results):
                st.image(img, caption=f"切り抜き結果 {i+1}", use_container_width=True)
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                buf.seek(0)
                st.download_button(
                    f"⬇️ ダウンロード {i+1}",
                    buf.getvalue(),
                    file_name=f"切り抜き_{i+1}.png",
                    mime="image/png"
                )
            
            if len(results) >= 2:
                zip_buf = io.BytesIO()
                with zipfile.ZipFile(zip_buf, 'w') as zf:
                    for i, img in enumerate(results):
                        buf = io.BytesIO()
                        img.save(buf, format="PNG")
                        zf.writestr(f"切り抜き_{i+1}.png", buf.getvalue())
                zip_buf.seek(0)
                st.download_button(
                    "📦 ZIPで一括ダウンロード",
                    zip_buf.getvalue(),
                    file_name=f"切り抜き_{datetime.now().strftime('%H%M')}.zip",
                    mime="application/zip"
                )
        else:
            st.error("❌ 処理できた画像がありませんでした")
            
