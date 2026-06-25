import streamlit as st
import io
from PIL import Image
import zipfile
from datetime import datetime
from birefnet import BiRefNet

st.set_page_config(page_title="西垣の切り抜き部屋", page_icon="✂️")

st.title("✂️ 西垣の切り抜き部屋（BiRefNet搭載）")
st.write("世界最高峰のAIで背景を除去します。最大5枚まで一括処理できます。")

# ===== BiRefNet モデル =====
@st.cache_resource
def get_model():
    return BiRefNet()

# ===== 画像リサイズ =====
def resize_image(img, max_size=800):
    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        return img.resize(new_size, Image.Resampling.LANCZOS)
    return img

# ===== UI =====
uploaded_files = st.file_uploader(
    "画像をアップロード（最大5枚）",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

if uploaded_files:
    if len(uploaded_files) > 5:
        st.warning("⚠️ 最大5枚までです。")
        uploaded_files = uploaded_files[:5]
    
    st.info(f"📸 {len(uploaded_files)}枚の画像を処理します")
    
    cols = st.columns(min(len(uploaded_files), 5))
    for idx, file in enumerate(uploaded_files[:5]):
        with cols[idx]:
            img = Image.open(file)
            img = resize_image(img, max_size=200)
            st.image(img, caption=file.name[:15], use_container_width=True)
    
    if st.button("✂️ 最強AIで背景除去！", use_container_width=True):
        processed = []
        failed = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        model = get_model()
        
        for i, uploaded_file in enumerate(uploaded_files):
            try:
                status_text.info(f"🔄 {i+1}/{len(uploaded_files)}枚目処理中: {uploaded_file.name}")
                
                img = Image.open(uploaded_file)
                original_size = img.size
                img = resize_image(img, max_size=800)
                
                # BiRefNetで背景除去
                result = model.remove_background(img)
                
                result = result.resize(original_size, Image.Resampling.LANCZOS)
                
                base_name = uploaded_file.name.rsplit('.', 1)[0]
                processed.append({
                    'name': f"{base_name}_切り抜き.png",
                    'image': result,
                    'original': uploaded_file.name
                })
                
                progress_bar.progress((i + 1) / len(uploaded_files))
                
            except Exception as e:
                failed.append({'name': uploaded_file.name, 'error': str(e)})
                progress_bar.progress((i + 1) / len(uploaded_files))
        
        status_text.empty()
        
        if processed:
            st.success(f"✅ {len(processed)}枚処理完了！")
            st.balloons()
            
            st.subheader("🖼️ 切り抜き結果")
            result_cols = st.columns(2)
            for idx, data in enumerate(processed):
                with result_cols[idx % 2]:
                    st.image(data['image'], caption=data['original'], use_container_width=True)
                    buf = io.BytesIO()
                    data['image'].save(buf, format='PNG')
                    buf.seek(0)
                    st.download_button(
                        label=f"⬇️ {data['name']}",
                        data=buf.getvalue(),
                        file_name=data['name'],
                        mime="image/png",
                        use_container_width=True,
                        key=f"dl_{idx}"
                    )
            
            if len(processed) >= 2:
                zip_buf = io.BytesIO()
                with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for data in processed:
                        img_bytes = io.BytesIO()
                        data['image'].save(img_bytes, format='PNG')
                        zf.writestr(data['name'], img_bytes.getvalue())
                zip_buf.seek(0)
                st.download_button(
                    label="📥 全ファイルをZIPでダウンロード",
                    data=zip_buf.getvalue(),
                    file_name=f"切り抜き_{datetime.now().strftime('%Y%m%d_%H%M')}.zip",
                    mime="application/zip",
                    use_container_width=True
                )
        
        if failed:
            with st.expander("⚠️ エラーが発生した画像"):
                for f in failed:
                    st.error(f"❌ {f['name']}: {f['error']}")
                
