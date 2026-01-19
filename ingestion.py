import os
import shutil

import kagglehub
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, Settings, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone

# import streamlit as st

load_dotenv()
llm = OpenAI()


if __name__ == "__main__":

    def ingest_data_set(folder_name: str, files_limit: int = 10) -> None:
        # INQUIRES PDF FILES WITH CV AND INGEST IT TO VECTOR DB
        documents = SimpleDirectoryReader(
            input_dir=f"./resume-docs/data/data/{folder_name}",
            num_files_limit=files_limit,
        ).load_data()

        print(f"📄 Завантажено документів: {len(documents)}")

        # Використовуємо SentenceSplitter для розбиття на chunks
        splitter = SentenceSplitter(chunk_size=1024, chunk_overlap=100)
        nodes = splitter.get_nodes_from_documents(documents)
        print(nodes[0])

        # Додаємо метадані: беремо doc_id з вихідного документа
        for doc in documents:
            for node in nodes:
                if node.node_id is not None and node.node_id == doc.doc_id:
                    node.metadata.update(
                        {
                            "file_name": os.path.basename(
                                doc.metadata.get("file_path", "")
                            ),
                            "resume_id": doc.doc_id,
                        }
                    )

        print(f"🔎 Створено нодів: {len(nodes)}")
        #
        Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0)
        Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

        pinecone = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
        pinecone_index = pinecone.Index("llamaindex-document-helper")
        vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        index = VectorStoreIndex(
            nodes, storage_context=storage_context, show_progress=True
        )

        print("✅ Data ingested and indexed successfully")

    def inquire_information(query_prompt: str) -> None:
        pinecone = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
        pinecone_index = pinecone.Index("llamaindex-document-helper")
        vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

        index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

        query_engine = index.as_query_engine()

        response = query_engine.query(query_prompt)

        print(response)

    # download_data_set()
    # ingest_data_set("DESIGNER", 20)
    inquire_information("How many candidates do we have?")