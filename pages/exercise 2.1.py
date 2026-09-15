import streamlit as st
import re
import os
import shutil
from pypdf import PdfReader

st.title("Exercise 2-1")

# 1. 上传文件
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # 提取文字
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += (page.extract_text() or "") + " "

    st.write(f"Total characters: {len(text)}")

    # 2. 让用户决定每块多大
    chunk_size = st.slider("Maximum chunk size (characters)",
                           min_value=200, max_value=3000, value=800, step=100)

    if st.button("Chunk document"):
        # 先拆成句子（在 . ! ? 后面断开）
        sentences = re.split(r'(?<=[.!?])\s+', text)

        # 把句子装进块里，装满就开新块
        chunks = []
        current = ""

        for sentence in sentences:
            if len(current) + len(sentence) <= chunk_size:
                current += sentence + " "
            else:
                if current:
                    chunks.append(current.strip())
                current = sentence + " "

        if current:                      # 别忘了最后一块
            chunks.append(current.strip())

        st.write(f"Created {len(chunks)} chunks")

        # 3. 保存每个 chunk 到项目目录下的 chunks 文件夹
        output_dir = "chunks"
        if os.path.exists(output_dir):    # 先清掉上一次的结果
            shutil.rmtree(output_dir)
        os.makedirs(output_dir)

        saved_paths = []
        for n, chunk in enumerate(chunks, start=1):
            path = os.path.join(output_dir, f"chunk_{n:03d}.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write(chunk)
            saved_paths.append(path)

        st.success(f"Saved {len(saved_paths)} chunks to ./{output_dir}/")

        # 4. 把保存的第一个 chunk 从硬盘读回来，存进变量
        first_path = saved_paths[0]
        with open(first_path, "r", encoding="utf-8") as f:
            first_chunk = f.read()

        # 5. 显示第一个 chunk
        st.subheader("First chunk (read back from file)")
        st.caption(f"Source: {first_path} — {len(first_chunk)} characters")
        st.write(first_chunk)

        # 完整列表
        st.subheader("All chunks")
        for n, chunk in enumerate(chunks):
            with st.expander(f"Chunk {n + 1} — {len(chunk)} characters"):
                st.write(chunk)