import streamlit as st
import streamlit_drawable_canvas as st_canvas
import io
from PIL import Image
import numpy as np

st.set_page_config(page_title="自由線で切り抜き", page_icon="✂️")

st.title("✂️ 自由線で囲って切り抜き")
st.write("画像の上を自由に線で囲んで、その内側だけを残します")

# ===== 画像リサイズ =====
def resize_image(img, max_size=600):
    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        return img.resize(new_size, Image.Resampling.LANCZOS)
    return img

# ===== 囲んだ部分だけを残す関数 =====
def keep_inside_mask(image, mask_data):
    """自由線で囲んだ内側だけを残す"""
    if mask_data is None:
        return image
    
    # RGBAに変換
    image = image.convert("RGBA")
    img_array = np.array(image)
    
    # マスクのRGB部分を取得
    mask = mask_data[:, :, :3]
    
    # 描画された部分（色が付いている部分）を検出
    drawn_mask = np.any(mask > 50, axis=2)
    
    # 描画された部分（内側）をそのまま残す
    # 外側を透明に（アルファチャンネルを0に）
    result = image.copy()
    result_array = np.array(result)
    
    # 描画されていない部分を透明に
    result_array[~drawn_mask, 3] = 0
    
    return Image.fromarray(result_array, "RGBA")

# ===== UI =====
uploaded_file = st.file_uploader(
    "画像をアップロード",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    # 画像を開く
    img = Image.open(uploaded_file)
    original_size = img.size
    img_display = resize_image(img, max_size=600)
    
    st.subheader("🖍️ 残したい部分を自由に囲んでね")
    st.write("マウスをドラッグして、残したい部分を囲んでください")
    
    # 描画キャンバス（自由線モード）
    canvas_result = st_canvas.st_canvas(
        fill_color="rgba(255, 0, 0, 0.1)",  # 囲んだ内側の塗りつぶし（薄い赤）
        stroke_width=3,
        stroke_color="#FF0000",  # 赤い線
        background_image=img_display,
        update_streamlit=True,
        height=img_display.height,
        width=img_display.width,
        drawing_mode="freedraw",  # ← これで自由線！
        key="freedraw_canvas",
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("✂️ 囲んだ内側を切り抜く！", use_container_width=True):
            if canvas_result.image_data is not None:
                with st.spinner("切り抜き中..."):
                    result = keep_inside_mask(img_display, canvas_result.image_data)
                    result = result.resize(original_size, Image.Resampling.LANCZOS)
                    
                    st.success("✅ 切り抜き完了！")
                    st.image(result, use_container_width=True)
                    
                    buf = io.BytesIO()
                    result.save(buf, format="PNG")
                    buf.seek(0)
                    st.download_button(
                        "⬇️ ダウンロード",
                        buf.getvalue(),
                        file_name="自由線で切り抜き.png",
                        mime="image/png"
                    )
            else:
                st.warning("⚠️ まず画像の上で自由に線を描いてください！")
