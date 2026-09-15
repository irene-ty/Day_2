import math
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import numpy as np

load_dotenv()

st.title("Exercise 2.4")

from pathlib import Path

import chromadb
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI


# 找到 Day_2 根目录和 .env
project_folder = Path(__file__).resolve().parents[1]
load_dotenv(project_folder / ".env")

client = OpenAI()

st.title("Exercise 2.4: Ask My Document with Chroma")

# Exercise 2.1 的 chunks 文件夹
chunks_folder = project_folder / "chunks"

if not chunks_folder.exists():
    st.error("Cannot find the chunks folder. Please run Exercise 2.1 first.")
    st.stop()

chunk_files = sorted(chunks_folder.glob("*.txt"))

if not chunk_files:
    st.error("No chunk files found.")
    st.stop()

# 建立本地 Chroma 向量数据库
chroma_client = chromadb.PersistentClient(
    path=str(project_folder / "chroma_database")
)

collection = chroma_client.get_or_create_collection(
    name="document_chunks"
)

# 把 2.1 的所有 chunks 存入 Chroma
# Chroma 会自动建立 embedding；upsert 可以避免重复加入相同资料
collection.upsert(
    ids=[file.stem for file in chunk_files],
    documents=[
        file.read_text(encoding="utf-8")
        for file in chunk_files
    ],
    metadatas=[
        {"source": file.name}
        for file in chunk_files
    ]
)

st.success(f"{len(chunk_files)} chunks are stored in Chroma.")

question = st.text_input("Ask a question about the document:")

if st.button("Ask document"):
    if not question.strip():
        st.warning("Please enter a question.")

    else:
        try:
            # Chroma 自动把问题转换为 embedding，
            # 并取回最相关的一个 chunk
            results = collection.query(
                query_texts=[question],
                n_results=1
            )

            retrieved_text = results["documents"][0][0]
            source_file = results["metadatas"][0][0]["source"]

            prompt = f"""
Answer the user's question using only the document excerpt below.

Question:
{question}

Document excerpt:
{retrieved_text}

Rules:
- Answer only using the document excerpt.
- If the excerpt does not contain the answer, say:
  "I cannot find the answer in the retrieved document section."
- End with this citation exactly:
  [Source: {source_file}]
"""

            response = client.responses.create(
                model="gpt-4o",
                input=prompt
            )

            st.subheader("Answer")
            st.write(response.output_text)

            st.subheader("Retrieved document source")
            st.write(f"Source file: `{source_file}`")

            with st.expander("Show the retrieved chunk"):
                st.write(retrieved_text)

        except Exception as error:
            st.error(f"Error: {error}")