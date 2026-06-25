import streamlit as st
import streamlit_drawable_canvas as st_canvas
import io
from PIL import Image
import numpy as np
from rembg import remove, new_session

st.set_page_config(page_title="西垣の切り抜き部屋 - 修正版", page_icon="✂️")

st.title("✂️ 西垣の切り抜き部屋（マウスで修正できる！）")
st.write("🟢 緑の円＝復活（残す） 🔴 赤の円＝削除（消す）")

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

# ===== マスクを画像に適用する関数（簡易版） =====
def apply_mask_to_image(image, mask_data):
    """マスクデータを使って画像を修正（簡易版）"""
    if mask_data is None:
        return image
    
    # RGBAに変換
    image = image.convert("RGBA")
    img_array = np.array(image)
    
    # マスクのRGB部分を取得
    mask = mask_data[:, :, :3]
    
    # 緑色（復活）と赤色（削除）を検出
    # 緑色の部分はそのまま、赤色の部分は透明に
    green_mask = (mask[:, :, 0] < 100) & (mask[:, :, 1] > 150) & (mask[:, :, 2] < 100)
    red_mask = (mask[:, :, 0] > 150) & (mask[:, :, 1] < 100) & (mask[:, :, 2] < 100)
    
    # 赤い部分を透明に
    img_array[red_mask, 3] = 0
    
    return Image.fromarray(img_array, "RGBA")

# ===== UI =====
uploaded_file = st.file_uploader(
    "画像をアップロード（1枚ずつ修正）",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    # 画像を開く
    img = Image.open(uploaded_file)
    original_size = img.size
    img_display = resize_image(img, max_size=600)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("元の画像")
        st.image(img_display, use_container_width=True)
    
    with col2:
        st.subheader("マスク（修正）")
        st.write("🟢 緑で描くと『復活』 🔴 赤で描くと『削除』")
        
        # ===== 描画キャンバス（エラー回避のため修正） =====
        try:
            canvas_result = st_canvas.st_canvas(
                fill_color="rgba(255, 0, 0, 0.3)",
                stroke_width=15,
                stroke_color="#00FF00",
                background_image=img_display,
                update_streamlit=True,
                height=img_display.height,
                width=img_display.width,
                drawing_mode="freedraw",
                key="canvas",
            )
        except Exception as e:
            st.error(f"キャンバスの読み込みでエラーが発生しました: {e}")
            canvas_result = None
    
    # ===== 処理ボタン =====
    if st.button("✂️ 切り抜き実行！", use_container_width=True):
        with st.spinner("処理中..."):
            try:
                # 1. rembgで大まかに切り抜き
                buf = io.BytesIO()
                img_display.save(buf, format="PNG")
                buf.seek(0)
                result_bytes = remove(buf.getvalue(), session=get_session())
                result = Image.open(io.BytesIO(result_bytes))
                
                # 2. マスク情報があれば適用
                if canvas_result is not None and canvas_result.image_data is not None:
                    result = apply_mask_to_image(result, canvas_result.image_data)
                
                # 3. 元のサイズに戻す
                if result.size != original_size:
                    result = result.resize(original_size, Image.Resampling.LANCZOS)
                
                # 4. 結果表示
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
                
            except Exception as e:
                st.error(f"処理中にエラーが発生しました: {e}")
