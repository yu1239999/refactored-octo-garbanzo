import streamlit as st
import io
from PIL import Image
import zipfile
from datetime import datetime

st.set_page_config(page_title="西垣の切り抜き部屋", page_icon="✂️")

st.title("✂️ 西垣の切り抜き部屋")
st.write("アップロードした画像の背景を切り抜きます。最大5枚まで一括処理できます。")

# ===== 5枚対応のアップロード =====
uploaded_files = st.file_uploader(
    "画像をアップロード（最大5枚）",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True  # ← これで複数選択OK！
)

if uploaded_files:
    # 5枚に制限
    if len(uploaded_files) > 5:
        st.warning("⚠️ 最大5枚までです。最初の5枚を処理します。")
        uploaded_files = uploaded_files[:5]
    
    st.info(f"📸 {len(uploaded_files)}枚の画像を処理します")
    
    # プレビュー表示
    cols = st.columns(min(len(uploaded_files), 5))
    for idx, file in enumerate(uploaded_files[:5]):
        with cols[idx]:
            img = Image.open(file)
            st.image(img, caption=file.name[:15], use_container_width=True)
    
    # ===== 処理ボタン =====
    if st.button("✂️ 切り抜き開始", use_container_width=True):
        processed = []
        failed = []
        
        # 進捗表示用
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, uploaded_file in enumerate(uploaded_files):
            try:
                status_text.info(f"🔄 {i+1}/{len(uploaded_files)}枚目処理中: {uploaded_file.name}")
                
                # 背景切り抜き（1枚版と同じ処理）
                from rembg import remove
                input_bytes = uploaded_file.getvalue()
                result_bytes = remove(input_bytes)
                result = Image.open(io.BytesIO(result_bytes))
                
                # ファイル名を生成
                base_name = uploaded_file.name.rsplit('.', 1)[0]
                processed.append({
                    'name': f"{base_name}_切り抜き.png",
                    'image': result,
                    'original': uploaded_file.name
                })
                
                progress_bar.progress((i + 1) / len(uploaded_files))
                
            except Exception as e:
                failed.append({
                    'name': uploaded_file.name,
                    'error': str(e)
                })
                progress_bar.progress((i + 1) / len(uploaded_files))
        
        status_text.empty()
        
        # ===== 結果表示 =====
        if processed:
            st.success(f"✅ {len(processed)}枚の画像を処理しました！")
            st.balloons()
            
            st.subheader("🖼️ 切り抜き結果")
            
            # 結果を2列で表示
            result_cols = st.columns(2)
            for idx, data in enumerate(processed):
                with result_cols[idx % 2]:
                    st.image(data['image'], caption=data['original'], use_container_width=True)
                    
                    # 個別ダウンロード
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
            
            # ===== ZIP一括ダウンロード =====
            if len(processed) >= 2:
                st.divider()
                st.subheader("📦 一括ダウンロード")
                
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
        
        # ===== エラー表示 =====
        if failed:
            with st.expander("⚠️ エラーが発生した画像"):
                for f in failed:
                    st.error(f"❌ {f['name']}: {f['error']}")
