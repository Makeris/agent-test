# import os
# from dotenv import load_dotenv
# from llama_index.core import (
#     SimpleDirectoryReader,
#     Settings,
#     StorageContext,
#     VectorStoreIndex,
#     Document,
# )
# from llama_index.core.node_parser import SentenceSplitter
# from llama_index.embeddings.openai import OpenAIEmbedding
# from llama_index.llms.openai import OpenAI
# from llama_index.vector_stores.pinecone import PineconeVectorStore
# from pinecone import Pinecone
#
#
# load_dotenv()
# llm = OpenAI()
#
#
# if __name__ == "__main__":

    # def ingest_data_set(files_limit: int = 15) -> None:
    #     # INQUIRES PDF FILES WITH CV AND INGEST IT TO VECTOR DB
    #     documents = SimpleDirectoryReader(
    #         input_dir="./examples",
    #         num_files_limit=files_limit,
    #     ).load_data()
    #
    #     print(f"📄 Завантажено документів: {len(documents)}")
    #
    #     # Використовуємо SentenceSplitter для розбиття на chunks
    #     splitter = SentenceSplitter(chunk_size=800, chunk_overlap=25)
    #     nodes = splitter.get_nodes_from_documents(documents)
    #     print(nodes[0])
    #
    #     # Додаємо метадані: беремо doc_id з вихідного документа
    #     for doc in documents:
    #         for node in nodes:
    #             if node.node_id is not None and node.node_id == doc.doc_id:
    #                 node.metadata.update(
    #                     {
    #                         "file_name": os.path.basename(
    #                             doc.metadata.get("file_path", "")
    #                         ),
    #                         "resume_id": doc.doc_id,
    #                     }
    #                 )
    #
    #     print(f"🔎 Створено нодів: {len(nodes)}")
    #     #
    #     Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0)
    #     Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
    #
    #     pinecone = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    #     pinecone_index = pinecone.Index("llamaindex-document-helper")
    #     vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    #
    #     storage_context = StorageContext.from_defaults(vector_store=vector_store)
    #
    #     index = VectorStoreIndex(
    #         nodes, storage_context=storage_context, show_progress=True
    #     )
    #
    #     print("Data ingested and indexed successfully")

#
# import candidates_list
#
# def ingest_vocabulary(vocabulary: list) -> None:
#     documents = [
#         Document(
#             text=f"{item['name']} — {item['role']}. {item['summary']} {item['info']}",
#             doc_id=str(item["id"]),
#             metadata={
#                 "type": "candidate",
#                 "candidate_id": str(item["id"]),
#                 "name": item.get("name", ""),
#                 "role": item.get("role", ""),
#                 "summary": item.get("summary", ""),
#             },
#         )
#         for item in vocabulary
#     ]
#
#     splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
#     nodes = splitter.get_nodes_from_documents(documents)
#
#     for doc in documents:
#         for node in nodes:
#             if node.ref_doc_id == doc.doc_id:
#                 node.metadata.update(doc.metadata)
#
#     Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0)
#     Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
#
#     pinecone = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
#     pinecone_index = pinecone.Index("llamaindex-document-helper")
#     vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
#
#     storage_context = StorageContext.from_defaults(vector_store=vector_store)
#
#     VectorStoreIndex(nodes, storage_context=storage_context, show_progress=True)
#
#     print("Candidates ingested and indexed successfully")
#
#
# import re
#
#
# def clean_text(text: str) -> str:
#     text = re.sub(r"\n\s*\n+", "\n\n", text)
#     text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
#     return text.strip()
#
#
# def preprocess_resume(text: str, name: str) -> str:
#     text = clean_text(text)
#
#     section_map = {
#         "PERSONAL INFORMATION": "## Personal Information",
#         "SOCIAL PROFILES": "## Social Profiles",
#         "LANGUAGES": "## Languages",
#         "SKILLS": "## Skills",
#         "WORK EXPERIENCE": "## Work Experience",
#         "EDUCATION": "## Education",
#         "COURSES": "## Courses",
#         "ACHIEVEMENTS": "## Achievements",
#         "ACCOMPLISHMENTS": "## Accomplishments",
#         "REFERENCES": "## References",
#     }
#     for old, new in section_map.items():
#         text = text.replace(old, new)
#
#     return f"# Resume: {name}\n\n{text}"
#
#
# def ingest_resumes(files_limit: int = 15) -> None:
#     documents = SimpleDirectoryReader(
#         input_dir="./examples",
#         num_files_limit=files_limit,
#     ).load_data()
#
#     print(f"📄 Loaded: {len(documents)}")
#
#     processed_documents = []
#     for doc in documents:
#         first_line = doc.text.split("\n")[0].strip()
#         clean_resume = preprocess_resume(doc.text, first_line)
#
#         metadata = {
#             "resume_id": doc.doc_id,
#             "owner": first_line,
#             "file_name": os.path.basename(doc.metadata.get("file_path", "")),
#         }
#
#         new_doc = Document(text=clean_resume, metadata=metadata, doc_id=doc.doc_id)
#         processed_documents.append(new_doc)
#
#     splitter = SentenceSplitter(chunk_size=510, chunk_overlap=100)
#     nodes = splitter.get_nodes_from_documents(processed_documents)
#
#     print(f"{len(nodes)}")
#
#     for doc in documents:
#         for node in nodes:
#             if node.ref_doc_id == doc.doc_id:
#                 node.metadata.update(
#                     {
#                         "resume_id": doc.doc_id,
#                         "owner": doc.text.split("\n")[0].strip(),
#                         "file_name": os.path.basename(
#                             doc.metadata.get("file_path", "")
#                         ),
#                     }
#                 )
#
#     Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0)
#     Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
#
#     pinecone = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
#     pinecone_index = pinecone.Index("llamaindex-document-helper")
#     vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
#
#     storage_context = StorageContext.from_defaults(vector_store=vector_store)
#
#     VectorStoreIndex(nodes, storage_context=storage_context, show_progress=True)
#
#
# # ingest_resumes()
# ingest_vocabulary(candidates_list.CANDIDATES)
