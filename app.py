import streamlit as st
import io
from PIL import Image
import zipfile
from datetime import datetime
from rembg import remove, new_session

st.set_page_config(page_title="商品切り抜き部屋", page_icon="📦")

st.title("📦 商品切り抜き部屋")
st.write("画像を小さくしてメモリを節約！")

# ===== 画像をリサイズする関数 =====
def resize_image(img, max_size=800):
    """メモリ節約のために画像をリサイズ"""
    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        return img.resize(new_size, Image.Resampling.LANCZOS)
    return img

@st.cache_resource
def get_session():
    return new_session("u2net")

uploaded_files = st.file_uploader(
    "商品画像を選んでね（小さい画像推奨）",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if uploaded_files:
    if len(uploaded_files) > 3:  # 5→3枚に減らす！
        st.warning("メモリ節約のため3枚までだよ！")
        uploaded_files = uploaded_files[:3]
    
    st.write(f"{len(uploaded_files)}枚 選択中")
    
    if st.button("切り抜く！"):
        results = []
        progress = st.progress(0)
        status = st.empty()
        session = get_session()
        
        for i, f in enumerate(uploaded_files):
            status.info(f"{i+1}/{len(uploaded_files)}枚目 処理中...")
            try:
                img = Image.open(f)
                
                # ===== メモリ節約：画像をリサイズ =====
                img = resize_image(img, max_size=800)
                
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
