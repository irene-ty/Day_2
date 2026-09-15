import math
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(env_path)
from openai import OpenAI

#1.Allows the user to copy and paste two different texts.

#2.Creates an embedding for each chunk of text. For this you will need to use the embedding function from the OpenAI API.

#3.Displays the cosine similarity of the two embeddings.

load_dotenv()
import math
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(env_path)

client = OpenAI()
client = OpenAI()

st.title("Text Similarity Checker")

text_1 = st.text_area("Text 1", height=150)
text_2 = st.text_area("Text 2", height=150)


def cosine_similarity(vector_1, vector_2):
    dot_product = sum(a * b for a, b in zip(vector_1, vector_2))
    length_1 = math.sqrt(sum(a * a for a in vector_1))
    length_2 = math.sqrt(sum(b * b for b in vector_2))

    return dot_product / (length_1 * length_2)


if st.button("Compare similarity"):
    if not text_1.strip() or not text_2.strip():
        st.warning("Please enter both texts.")
    else:
        response = client.embeddings.create(
            model="text-embedding-3-large",
            input=[text_1, text_2]
        )

        embedding_1 = response.data[0].embedding
        embedding_2 = response.data[1].embedding

        similarity = cosine_similarity(embedding_1, embedding_2)

        st.success(f"Cosine similarity: {similarity:.3f}")

        if similarity > 0.8:
            st.write("The two texts are very similar.")
        elif similarity > 0.5:
            st.write("The two texts are somewhat related.")
        else:
            st.write("The two texts are not very similar.")