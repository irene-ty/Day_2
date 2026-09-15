import streamlit as st
import re
from pypdf import PdfReader

st.title("Exercise 2-1")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # 1. 提取文字
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += (page.extract_text() or "") + " "

    st.write(f"Total characters: {len(text)}")

    # 2. 让用户决定每块多大
    chunk_size = st.slider("Maximum chunk size (characters)",
                           min_value=200, max_value=3000, value=800, step=100)

    if st.button("Chunk document"):
        # 3. 先拆成句子（在 . ! ? 后面断开）
        sentences = re.split(r'(?<=[.!?])\s+', text)

        # 4. 把句子装进块里，装满就开新块
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

        # 5. 显示结果
        st.write(f"Created {len(chunks)} chunks")

        for n, chunk in enumerate(chunks):
            with st.expander(f"Chunk {n + 1} — {len(chunk)} characters"):
                st.write(chunk)