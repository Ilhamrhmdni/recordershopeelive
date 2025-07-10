import streamlit as st
import subprocess
import datetime
from pathlib import Path

st.set_page_config(page_title="Shopee Live Recorder", layout="centered")
st.title("📺 Shopee Live Multi Link Recorder")

# Folder output video
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

# Input link Shopee Live
st.subheader("🔗 Masukkan Link Shopee Live (.flv)")
link_input = st.text_area("Pisahkan setiap link dengan baris baru")
duration = st.text_input("⏱️ Durasi Rekaman (format HH:MM:SS)", value="00:05:00")

if st.button("🎬 Mulai Rekam"):
    links = [line.strip() for line in link_input.splitlines() if line.strip()]
    if not links:
        st.warning("⚠️ Masukkan setidaknya satu link Shopee Live.")
    else:
        st.info(f"Memulai rekaman {len(links)} video live...")
        for i, url in enumerate(links):
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"shopee_live_{i+1}_{timestamp}.mp4"
            filepath = output_dir / filename

            command = [
                "ffmpeg", "-y",
                "-i", url,
                "-c", "copy",
                "-t", duration,
                str(filepath)
            ]

            with st.status(f"⏺️ Merekam link ke-{i+1}..."):
                result = subprocess.run(command, capture_output=True, text=True)
                if result.returncode == 0:
                    st.success(f"✅ Selesai: {filename}")
                    with open(filepath, "rb") as f:
                        st.download_button(f"📥 Download {filename}", f, file_name=filename)
                else:
                    st.error(f"❌ Gagal merekam link ke-{i+1}")
                    st.code(result.stderr, language="bash")
