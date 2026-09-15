import math
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI


# 找到 Day_2 根目录和 .env 文件
project_folder = Path(__file__).resolve().parents[1]
load_dotenv(project_folder / ".env")

client = OpenAI()

st.title("Exercise 2.3: Ask My Document")

# 读取 Exercise 2.1 创建的所有 chunks
chunks_folder = project_folder / "chunks"

if not chunks_folder.exists():
    st.error("Cannot find the chunks folder. Please run Exercise 2.1 first.")
    st.stop()

chunk_files = sorted(chunks_folder.glob("*.txt"))

if not chunk_files:
    st.error("No .txt chunks found in the chunks folder.")
    st.stop()

chunk_texts = [
    file.read_text(encoding="utf-8")
    for file in chunk_files
]


def cosine_similarity(vector_1, vector_2):
    dot_product = sum(a * b for a, b in zip(vector_1, vector_2))
    length_1 = math.sqrt(sum(a * a for a in vector_1))
    length_2 = math.sqrt(sum(b * b for b in vector_2))

    return dot_product / (length_1 * length_2)


question = st.text_input("Ask a question about the document:")

if st.button("Ask document"):
    if not question.strip():
        st.warning("Please enter a question.")

    else:
        try:
            # 为问题和每一个 chunk 创建 embedding
            embedding_response = client.embeddings.create(
                model="text-embedding-3-large",
                input=[question] + chunk_texts
            )

            question_embedding = embedding_response.data[0].embedding
            chunk_embeddings = [
                item.embedding
                for item in embedding_response.data[1:]
            ]

            # 计算问题与每一个 chunk 的相似度
            scores = [
                cosine_similarity(question_embedding, chunk_embedding)
                for chunk_embedding in chunk_embeddings
            ]

            # 找出分数最高的 chunk
            best_index = scores.index(max(scores))
            best_chunk = chunk_texts[best_index]
            best_file = chunk_files[best_index]

            # 只把最相关的内容交给模型回答
            prompt = f"""
Answer the user's question using only the document excerpt below.

Question:
{question}

Document excerpt:
{best_chunk}

Rules:
- Answer only using the document excerpt.
- If the excerpt does not contain the answer, say:
  "I cannot find the answer in the retrieved document section."
- End your answer with this citation exactly:
  [Source: {best_file.name}]
"""

            answer_response = client.responses.create(
                model="gpt-4o",
                input=prompt
            )

            st.subheader("Answer")
            st.write(answer_response.output_text)

            st.subheader("Retrieved source")
            st.write(f"File: `{best_file.name}`")
            st.write(f"Cosine similarity: {scores[best_index]:.3f}")

            with st.expander("Show document excerpt used for this answer"):
                st.write(best_chunk)

        except Exception as error:
            st.error(f"OpenAI API error: {error}")