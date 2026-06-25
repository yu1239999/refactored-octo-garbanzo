import streamlit as st
from PIL import Image
import io
import zipfile
from datetime import datetime
from carvekit import Interface

st.set_page_config(
    page_title="🐾 ぱぱっと切り抜き動物園（CarveKit）",
    page_icon="🦁",
    layout="wide"
)

st.title("🐾 ぱぱっと切り抜き動物園（CarveKit）")
st.write("CarveKitを使って背景を切り抜くよ！")

@st.cache_resource
def get_interface():
    return Interface()

uploaded_files = st.file_uploader(
    "画像を選択（JPG・PNG）",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if uploaded_files:
    if len(uploaded_files) > 5:
        st.warning("⚠️ 最大5枚までです。最初の5枚を処理します。")
        uploaded_files = uploaded_files[:5]
    
    st.info(f"📸 {len(uploaded_files)}枚の画像を処理します")
    
    cols = st.columns(min(len(uploaded_files), 5))
    for idx, file in enumerate(uploaded_files[:5]):
        with cols[idx]:
            img = Image.open(file)
            st.image(img, caption=f"{file.name[:15]}...", use_container_width=True)
    
    if st.button("✂️ 切り抜き開始", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        processed = []
        failed = []
        interface = get_interface()
        
        for i, file in enumerate(uploaded_files):
            try:
                status_text.info(f"🔄 {i+1}/{len(uploaded_files)}枚目処理中: {file.name}")
                
                img = Image.open(file)
                
                # CarveKitで背景除去！
                result_img = interface([img])[0]
                
                base_name = file.name.rsplit('.', 1)[0]
                processed.append({
                    'name': f"{base_name}_切り抜き.png",
                    'image': result_img,
                    'original': file.name
                })
                
                progress_bar.progress((i + 1) / len(uploaded_files))
                
            except Exception as e:
                failed.append({'name': file.name, 'error': str(e)})
                progress_bar.progress((i + 1) / len(uploaded_files))
        
        status_text.empty()
        
        if processed:
            st.success(f"✅ {len(processed)}枚の画像を処理しました！")
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
            
            if processed:
                zip_buf = io.BytesIO()
                with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for data in processed:
                        img_bytes = io.BytesIO()
                        data['image'].save(img_bytes, format='PNG')
                        zf.writestr(data['name'], img_bytes.getvalue())
                
                zip_buf.seek(0)
                
                st.divider()
                st.subheader("📦 一括ダウンロード")
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
