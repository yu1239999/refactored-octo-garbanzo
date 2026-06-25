import streamlit as st
import io
from PIL import Image
import zipfile
from datetime import datetime
from rembg import remove, new_session

st.set_page_config(page_title="西垣の切り抜き部屋 - 拡大版", page_icon="🔍")

st.title("🔍 西垣の切り抜き部屋（拡大してから切り抜き）")
st.write("画像を拡大して背景を消しやすくしてから、元のサイズに戻します。")

# ===== 画像を拡大（ズーム）する関数 =====
def zoom_image(img, zoom_factor=1.3):
    """
    画像を中心から拡大（ズーム）する
    zoom_factor: 1.0〜2.0（1.3くらいがおすすめ）
    """
    w, h = img.size
    new_w = int(w / zoom_factor)
    new_h = int(h / zoom_factor)
    
    # 中心を切り抜く
    left = (w - new_w) // 2
    top = (h - new_h) // 2
    right = left + new_w
    bottom = top + new_h
    
    cropped = img.crop((left, top, right, bottom))
    
    # 元のサイズに拡大
    return cropped.resize((w, h), Image.Resampling.LANCZOS)

# ===== AIセッション =====
@st.cache_resource
def get_session():
    return new_session("u2net_human_seg")

# ===== UI =====
uploaded_files = st.file_uploader(
    "商品画像をアップロード（最大5枚）",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

if uploaded_files:
    if len(uploaded_files) > 5:
        st.warning("⚠️ 最大5枚までです。")
        uploaded_files = uploaded_files[:5]
    
    st.info(f"📸 {len(uploaded_files)}枚の画像を処理します")
    
    zoom_factor = st.slider(
        "拡大倍率（数値を上げると商品が大きく映ります）",
        min_value=1.0,
        max_value=2.0,
        value=1.3,
        step=0.05,
        help="1.3倍くらいがおすすめ。大きくしすぎると商品の一部が切れます"
    )
    
    cols = st.columns(min(len(uploaded_files), 5))
    for idx, file in enumerate(uploaded_files[:5]):
        with cols[idx]:
            img = Image.open(file)
            st.image(img, caption=f"元画像: {file.name[:15]}", use_container_width=True)
    
    if st.button("✂️ 拡大してから切り抜く！", use_container_width=True):
        processed = []
        failed = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        session = get_session()
        
        for i, uploaded_file in enumerate(uploaded_files):
            try:
                status_text.info(f"🔄 {i+1}/{len(uploaded_files)}枚目処理中: {uploaded_file.name}")
                
                # 1. 画像を開く
                img = Image.open(uploaded_file)
                original_size = img.size  # ← 元のサイズを保存！
                
                # 2. 拡大（ズーム）する！
                img_zoomed = zoom_image(img, zoom_factor=zoom_factor)
                
                # 3. rembgで背景切り抜き（拡大状態でやる）
                buf = io.BytesIO()
                img_zoomed.save(buf, format="PNG")
                buf.seek(0)
                result_bytes = remove(buf.getvalue(), session=session)
                result_zoomed = Image.open(io.BytesIO(result_bytes))
                
                # 4. 元のサイズに縮小する！ ← ここが重要！
                result = result_zoomed.resize(original_size, Image.Resampling.LANCZOS)
                
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
            
            st.subheader("🖼️ 切り抜き結果（元のサイズに戻しました）")
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
                    label="📥 ZIPで一括ダウンロード",
                    data=zip_buf.getvalue(),
                    file_name=f"切り抜き_{datetime.now().strftime('%Y%m%d_%H%M')}.zip",
                    mime="application/zip",
                    use_container_width=True
                )
        
        if failed:
            with st.expander("⚠️ エラーが発生した画像"):
                for f in failed:
                    st.error(f"❌ {f['name']}: {f['error']}")
