import streamlit as st
import io
from PIL import Image
import zipfile
from datetime import datetime
from rembg import remove

st.set_page_config(page_title="西垣の切り抜き部屋", page_icon="✂️")

st.title("✂️ 西垣の切り抜き部屋")
st.write("最大5枚まで一括で背景を削除します")

uploaded_files = st.file_uploader(
    "画像をアップロード（最大5枚）",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

if uploaded_files:
    if len(uploaded_files) > 5:
        st.warning("⚠️ 最大5枚までです")
        uploaded_files = uploaded_files[:5]
    
    st.info(f"📸 {len(uploaded_files)}枚の画像を処理します")
    
    # プレビュー
    cols = st.columns(min(len(uploaded_files), 5))
    for idx, file in enumerate(uploaded_files[:5]):
        with cols[idx]:
            img = Image.open(file)
            st.image(img, caption=file.name[:15], use_container_width=True)
    
    if st.button("✂️ 背景削除！", use_container_width=True):
        processed = []
        failed = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, file in enumerate(uploaded_files):
            try:
                status_text.info(f"🔄 {i+1}/{len(uploaded_files)}枚目処理中: {file.name}")
                
                # 背景削除
                result_bytes = remove(file.getvalue())
                result = Image.open(io.BytesIO(result_bytes))
                
                base_name = file.name.rsplit('.', 1)[0]
                processed.append({
                    'name': f"{base_name}_切り抜き.png",
                    'image': result,
                    'original': file.name
                })
                
                progress_bar.progress((i + 1) / len(uploaded_files))
                
            except Exception as e:
                failed.append({'name': file.name, 'error': str(e)})
                progress_bar.progress((i + 1) / len(uploaded_files))
        
        status_text.empty()
        
        if processed:
            st.success(f"✅ {len(processed)}枚処理完了！")
            st.balloons()
            
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
                    label="📥 ZIPで一括ダウンロード",
                    data=zip_buf.getvalue(),
                    file_name=f"切り抜き_{datetime.now().strftime('%Y%m%d_%H%M')}.zip",
                    mime="application/zip"
                )
        
        if failed:
            with st.expander("⚠️ エラーが発生した画像"):
                for f in failed:
                    st.error(f"❌ {f['name']}: {f['error']}")
                    
