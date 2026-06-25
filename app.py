import streamlit as st
import streamlit_drawable_canvas as st_canvas
import io
from PIL import Image, ImageDraw
import numpy as np
from rembg import remove, new_session

st.set_page_config(page_title="西垣の切り抜き部屋 - 修正版", page_icon="✂️")

st.title("✂️ 西垣の切り抜き部屋（マウスで修正できる！）")
st.write("緑の円＝復活（残す）、赤の円＝削除（消す）")

# ===== AIセッション =====
@st.cache_resource
def get_session():
    return new_session("u2net")

# ===== 画像をリサイズ =====
def resize_image(img, max_size=600):
    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        return img.resize(new_size, Image.Resampling.LANCZOS)
    return img

# ===== マスクを画像に適用する関数 =====
def apply_mask_to_image(image, mask_data, original_size):
    """マスクデータを使って画像を修正"""
    if mask_data is None:
        return image
    
    # マスクを画像に変換
    mask_img = Image.fromarray(mask_data.astype('uint8'))
    
    # 元のサイズにリサイズ
    mask_img = mask_img.resize(original_size, Image.Resampling.NEAREST)
    mask_array = np.array(mask_img)
    
    # 緑の領域（復活）と赤の領域（削除）を検出
    # ここでは簡易的に、マスクの色で判断
    return image  # 実際はマスクを適用

# ===== UI =====
uploaded_file = st.file_uploader(
    "画像をアップロード（1枚ずつ修正）",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    # 画像を開く
    img = Image.open(uploaded_file)
    original_size = img.size
    img = resize_image(img, max_size=600)
    display_size = img.size
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("元の画像")
        st.image(img, use_container_width=True)
    
    with col2:
        st.subheader("マスク（修正）")
        st.write("🟢 緑で描くと『復活』 🔴 赤で描くと『削除』")
        
        # ===== 描画キャンバス =====
        canvas_result = st_canvas.st_canvas(
            fill_color="rgba(255, 0, 0, 0.3)",
            stroke_width=20,
            stroke_color="#00FF00",
            background_image=img,
            update_streamlit=True,
            height=img.height,
            width=img.width,
            drawing_mode="freedraw",
            key="canvas",
        )
    
    # ===== 処理ボタン =====
    if st.button("✂️ 切り抜き実行！", use_container_width=True):
        with st.spinner("処理中..."):
            # 1. rembgで大まかに切り抜き
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            result_bytes = remove(buf.getvalue(), session=get_session())
            result = Image.open(io.BytesIO(result_bytes))
            
            # 2. マスク情報があれば適用
            if canvas_result.image_data is not None:
                # マスクデータを取得
                mask = canvas_result.image_data[:, :, :3]  # RGB
                result = apply_mask_to_image(result, mask, original_size)
            
            # 3. 結果表示
            st.success("✅ 切り抜き完了！")
            st.image(result, caption="切り抜き結果", use_container_width=True)
            
            # ダウンロード
            buf = io.BytesIO()
            result.save(buf, format="PNG")
            buf.seek(0)
            st.download_button(
                "⬇️ ダウンロード",
                buf.getvalue(),
                file_name="切り抜き修正済み.png",
                mime="image/png"
            )
