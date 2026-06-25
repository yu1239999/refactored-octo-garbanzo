import streamlit as st
from rembg import remove
from PIL import Image
import io
import zipfile
from datetime import datetime

st.set_page_config(
    page_title="✂️ 西垣の切り抜き部屋",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===== 和風モダンCSS =====
st.markdown("""
<style>
    /* ベース */
    .stApp {
        background: #f5f0eb !important;
    }
    
    /* メインコンテナ */
    .main {
        max-width: 1100px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    /* ヘッダー */
    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.5rem 0;
        border-bottom: 2px solid #e8e0d8;
        margin-bottom: 2.5rem;
    }
    
    .header-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #2d2a24;
        letter-spacing: 2px;
    }
    
    .header-title .scissors {
        color: #c0392b;
        margin-right: 0.5rem;
    }
    
    .header-sub {
        color: #8b7a6b;
        font-size: 0.85rem;
        letter-spacing: 1px;
        background: #e8e0d8;
        padding: 0.3rem 1rem;
        border-radius: 50px;
    }
    
    /* ヒーロー */
    .hero {
        background: white;
        border-radius: 16px;
        padding: 3rem;
        margin-bottom: 2.5rem;
        box-shadow: 0 2px 20px rgba(0,0,0,0.04);
        text-align: center;
    }
    
    .hero h1 {
        font-size: 3rem;
        font-weight: 700;
        color: #2d2a24;
        margin: 0;
        letter-spacing: 3px;
    }
    
    .hero h1 span {
        color: #c0392b;
    }
    
    .hero p {
        color: #8b7a6b;
        font-size: 1rem;
        margin-top: 0.8rem;
        letter-spacing: 1px;
    }
    
    /* アップロードエリア */
    .upload-area {
        border: 2px dashed #d5cdc5;
        border-radius: 16px;
        padding: 3.5rem 2rem;
        text-align: center;
        background: white;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .upload-area:hover {
        border-color: #c0392b;
        background: #fdf8f5;
    }
    
    .upload-area .icon {
        font-size: 3.5rem;
        margin-bottom: 0.5rem;
    }
    
    .upload-area h3 {
        color: #2d2a24;
        font-weight: 500;
        margin: 0.5rem 0;
    }
    
    .upload-area p {
        color: #b5aa9f;
        font-size: 0.9rem;
        margin: 0;
    }
    
    /* ファイル情報 */
    .file-info {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: white;
        padding: 0.8rem 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 1px 10px rgba(0,0,0,0.04);
    }
    
    .file-count {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #2d2a24;
        font-weight: 500;
    }
    
    .file-count .num {
        background: #c0392b;
        color: white;
        padding: 0.1rem 0.6rem;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 700;
    }
    
    .file-names {
        color: #8b7a6b;
        font-size: 0.85rem;
    }
    
    /* ボタン - 和風 */
    .stButton > button {
        background: #2d2a24 !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
        letter-spacing: 2px !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        background: #c0392b !important;
        transform: scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(192, 57, 43, 0.25) !important;
    }
    
    /* ダウンロードボタン */
    .download-btn > button {
        background: white !important;
        color: #2d2a24 !important;
        border: 1px solid #d5cdc5 !important;
    }
    
    .download-btn > button:hover {
        background: #c0392b !important;
        color: white !important;
        border-color: #c0392b !important;
    }
    
    /* プログレス */
    .stProgress > div > div {
        background: #e8e0d8 !important;
        height: 4px !important;
        border-radius: 50px !important;
    }
    
    .stProgress > div > div > div {
        background: #c0392b !important;
        height: 4px !important;
        border-radius: 50px !important;
    }
    
    /* ステータス */
    .status-box {
        background: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        display: flex;
        align-items: center;
        gap: 1rem;
        box-shadow: 0 1px 10px rgba(0,0,0,0.04);
    }
    
    .status-box .spinner {
        width: 18px;
        height: 18px;
        border: 2px solid #e8e0d8;
        border-top: 2px solid #c0392b;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .status-box .text {
        color: #2d2a24;
        font-size: 0.9rem;
    }
    
    /* 結果カード */
    .result-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 2px 15px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .result-card:hover {
        box-shadow: 0 4px 25px rgba(0,0,0,0.08);
    }
    
    .result-label {
        color: #b5aa9f;
        font-size: 0.7rem;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    
    /* 成功メッセージ */
    .success-msg {
        background: #f0f7f0;
        color: #2d6a3e;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        text-align: center;
        font-weight: 500;
        margin: 1rem 0;
    }
    
    /* フッター */
    .footer {
        text-align: center;
        padding: 2.5rem 0 1rem;
        color: #c5bab0;
        font-size: 0.8rem;
        letter-spacing: 1px;
        border-top: 1px solid #e8e0d8;
        margin-top: 3rem;
    }
    
    /* 画像グリッド */
    .grid-preview {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    /* レスポンシブ */
    @media (max-width: 768px) {
        .header {
            flex-direction: column;
            gap: 1rem;
            text-align: center;
        }
        .hero h1 {
            font-size: 2rem;
        }
        .hero {
            padding: 2rem 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ===== ヘッダー =====
st.markdown("""
<div class="header">
    <div class="header-title">
        <span class="scissors">✂️</span>西垣の切り抜き部屋
    </div>
    <div class="header-sub">
        背景切り抜き専門店
    </div>
</div>
""", unsafe_allow_html=True)

# ===== ヒーロー =====
st.markdown("""
<div class="hero">
    <h1>画像を<span>ぱぱっと</span>切り抜き</h1>
    <p>最大5枚までまとめて処理できます</p>
</div>
""", unsafe_allow_html=True)

# ===== メイン処理 =====
MAX_FILES = 5

uploaded_files = st.file_uploader(
    "",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
    label_visibility="collapsed"
)

if not uploaded_files:
    st.markdown("""
    <div class="upload-area">
        <div class="icon">🖼️</div>
        <h3>画像をドロップしてください</h3>
        <p>またはクリックして選択 ｜ JPG・PNG ｜ 最大5枚</p>
    </div>
    """, unsafe_allow_html=True)

if uploaded_files:
    if len(uploaded_files) > MAX_FILES:
        st.warning(f"⚠️ 最大{MAX_FILES}枚までです。最初の{MAX_FILES}枚を処理します。")
        uploaded_files = uploaded_files[:MAX_FILES]
    
    # ファイル情報
    names = []
    for f in uploaded_files[:5]:
        name = f.name[:12] + "..." if len(f.name) > 12 else f.name
        names.append(name)
    
    st.markdown(f"""
    <div class="file-info">
        <div class="file-count">
            <span class="num">{len(uploaded_files)}</span> 枚の画像
        </div>
        <div class="file-names">
            {', '.join(names)}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # プレビュー
    cols = st.columns(min(len(uploaded_files), 5))
    for idx, file in enumerate(uploaded_files[:5]):
        with cols[idx]:
            img = Image.open(file)
            st.image(img, use_container_width=True)
            st.caption(f"📷 {file.name[:10]}...")
    
    # 処理ボタン
    if st.button("✂️ 切り抜き開始", use_container_width=True):
        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        
        processed = []
        failed = []
        
        for i, file in enumerate(uploaded_files):
            try:
                status_placeholder.markdown(f"""
                <div class="status-box">
                    <div class="spinner"></div>
                    <div class="text">
                        {i+1}/{len(uploaded_files)}枚目 処理中… {file.name}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                result_bytes = remove(file.getvalue())
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
        
        status_placeholder.empty()
        
        if processed:
            st.markdown("""
            <div class="success-msg">
                ✅ 切り抜き完了！ 全 {} 枚処理しました
            </div>
            """.format(len(processed)), unsafe_allow_html=True)
            
            st.balloons()
            
            # 結果表示
            st.markdown("### 🎨 切り抜き結果")
            
            result_cols = st.columns(2)
            for idx, data in enumerate(processed):
                with result_cols[idx % 2]:
                    st.markdown(f"""
                    <div class="result-card">
                        <div class="result-label">📎 {data['original']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.image(data['image'], use_container_width=True)
                    
                    # 個別ダウンロード
                    buf = io.BytesIO()
                    data['image'].save(buf, format='PNG')
                    buf.seek(0)
                    
                    st.download_button(
                        label="⬇️ ダウンロード",
                        data=buf.getvalue(),
                        file_name=data['name'],
                        mime="image/png",
                        use_container_width=True,
                        key=f"dl_{idx}"
                    )
            
            # ZIPダウンロード
            if processed:
                zip_buf = io.BytesIO()
                with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for data in processed:
                        img_bytes = io.BytesIO()
                        data['image'].save(img_bytes, format='PNG')
                        zf.writestr(data['name'], img_bytes.getvalue())
                
                zip_buf.seek(0)
                
                st.markdown("---")
                st.markdown("### 📦 まとめてダウンロード")
                
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

# ===== フッター =====
st.markdown("""
<div class="footer">
    ✂️ 西垣の切り抜き部屋 ｜ 背景切り抜き専門
</div>
""", unsafe_allow_html=True)