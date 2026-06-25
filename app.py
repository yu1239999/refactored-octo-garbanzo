import streamlit as st
from rembg import remove, new_session
from PIL import Image
import io
import zipfile
from datetime import datetime

st.set_page_config(
    page_title="🐾 ぱぱっと切り抜き動物園",
    page_icon="🦁",
    layout="wide"
)

# ===== かわいいCSS（略） =====
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #fdf6e3, #f5e6d3) !important; }
    .main-header { text-align: center; padding: 1.5rem; background: rgba(255,255,255,0.7); border-radius: 30px; margin-bottom: 2rem; box-shadow: 0 8px 32px rgba(0,0,0,0.08); }
    .main-header h1 { font-size: 3rem; font-weight: 900; color: #2d2a24; letter-spacing: 2px; }
    .main-header h1 span { color: #e67e22; }
    .animal-emoji { font-size: 2.5rem; display: inline-block; animation: bounce 2s infinite; }
    @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
    .cute-box { background: rgba(255,255,255,0.8); border-radius: 25px; padding: 1.5rem; margin: 1rem 0; border: 3px dashed #f1c40f; text-align: center; }
    .cute-box .big-emoji { font-size: 4rem; }
    .cute-box p { font-size: 1.2rem; color: #2d2a24; font-weight: 500; }
    .stButton > button { background: linear-gradient(135deg, #f39c12, #e67e22) !important; color: white !important; border: none !important; border-radius: 50px !important; padding: 0.8rem 2rem !important; font-weight: 700 !important; font-size: 1.1rem !important; transition: all 0.3s ease !important; letter-spacing: 1px !important; width: 100% !important; }
    .stButton > button:hover { transform: scale(1.05) !important; box-shadow: 0 8px 30px rgba(230, 126, 34, 0.4) !important; }
    .animal-badge { display: inline-block; background: #f1c40f; color: #2d2a24; padding: 0.2rem 1rem; border-radius: 50px; font-weight: 700; font-size: 0.8rem; }
    .footer { text-align: center; padding: 2rem 0 1rem; color: #8b7a6b; font-size: 0.9rem; }
    .footer .animal { font-size: 1.2rem; }
</style>
""", unsafe_allow_html=True)

# ===== ヘッダー =====
st.markdown("""
<div class="main-header">
    <div><span class="animal-emoji">🦁</span><span class="animal-emoji">🐯</span><span class="animal-emoji">🐻</span><span class="animal-emoji">🐼</span><span class="animal-emoji">🐨</span></div>
    <h1>🐾 ぱぱっと<span>切り抜き</span>動物園</h1>
    <p style="color:#8b7a6b; font-size:1.1rem;">🎪 画像を入れると、背景をぱぱっと切り抜いちゃうよ！</p>
    <p><span class="animal-badge">🦊 最大5枚まで</span><span class="animal-badge">🐼 無料</span><span class="animal-badge">🐨 かんたん</span></p>
</div>
""", unsafe_allow_html=True)

# ===== アップロードエリア =====
st.markdown("""
<div class="cute-box">
    <div class="big-emoji">📸</div>
    <p>🐘 画像を選んでね！</p>
</div>
""", unsafe_allow_html=True)

# ===== モデル選択 =====
model_option = st.selectbox(
    "🤖 使用するAIモデルを選んでね",
    ["u2net_cloth_seg", "birefnet-general", "birefnet-dis", "birefnet-massive", "u2net_human_seg"]
)

@st.cache_resource
def get_session(model_name):
    return new_session(model_name)

uploaded_files = st.file_uploader(
    "📸 画像を選んでね（JPG・PNG）",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
    label_visibility="visible"
)

if uploaded_files:
    if len(uploaded_files) > 5:
        st.warning("⚠️ 5枚までだよ！最初の5枚を処理するね 🐼")
        uploaded_files = uploaded_files[:5]
    
    st.info(f"📸 {len(uploaded_files)}枚の画像を処理するよ！ 🐾")
    
    cols = st.columns(min(len(uploaded_files), 5))
    for idx, file in enumerate(uploaded_files[:5]):
        with cols[idx]:
            img = Image.open(file)
            st.image(img, caption=f"📷 {file.name[:15]}...", use_container_width=True)
    
    if st.button("✂️ ぱぱっと切り抜く！ 🐾", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        processed = []
        failed = []
        
        animal_icons = ["🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼", "🐨", "🐯", "🦁", "🐮", "🐷"]
        session = get_session(model_option)
        
        for i, file in enumerate(uploaded_files):
            try:
                animal = animal_icons[i % len(animal_icons)]
                status_text.info(f"{animal} {i+1}/{len(uploaded_files)}枚目 処理中… {file.name}")
                
                img = Image.open(file)
                
                buf = io.BytesIO()
                img.save(buf, format='PNG')
                buf.seek(0)
                
                result_bytes = remove(buf.getvalue(), session=session)
                result_img = Image.open(io.BytesIO(result_bytes))
                
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
            st.balloons()
            st.success(f"🎉 {len(processed)}枚 切り抜き完了！ 🐾")
            
            st.subheader("🖼️ 切り抜き結果 🎪")
            
            result_cols = st.columns(2)
            for idx, data in enumerate(processed):
                with result_cols[idx % 2]:
                    st.image(data['image'], caption=f"{animal_icons[idx % len(animal_icons)]} {data['original']}", use_container_width=True)
                    
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
                st.subheader("📦 まとめてダウンロード 🐘")
                st.download_button(
                    label="📥 全ファイルをZIPでダウンロード",
                    data=zip_buf.getvalue(),
                    file_name=f"切り抜き_{datetime.now().strftime('%Y%m%d_%H%M')}.zip",
                    mime="application/zip",
                    use_container_width=True
                )
        
        if failed:
            with st.expander("⚠️ エラーになった画像 🐾"):
                for f in failed:
                    st.error(f"❌ {f['name']}: {f['error']}")

st.markdown("""
<div class="footer">
    <span class="animal">🐾</span>
    ぱぱっと切り抜き動物園 ｜ 背景切り抜き専門 🐘
    <span class="animal">🐾</span>
</div>
""", unsafe_allow_html=True)
