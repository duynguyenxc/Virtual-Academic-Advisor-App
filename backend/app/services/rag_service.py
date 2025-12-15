from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.msgs import HumanMessage, SystemMessage
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv

# Load env vars
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"))
from app.core.database import DATABASE_URL

class RAGService:
    def __init__(self):
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY is missing")

        # 1. Setup Embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004", 
            google_api_key=google_api_key
        )

        # 2. Setup Vector Store
        connection_string = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")
        self.vector_store = PGVector(
            embeddings=self.embeddings,
            collection_name="olemiss_knowledge_base_gemini",
            connection=connection_string,
            use_jsonb=True,
        )
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})

        # 3. Setup LLM (Gemini)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=0.3,
            google_api_key=google_api_key
        )

        # 4. Prompt Template
        self.template = """You are an expert Academic Advisor for Computer Science students at Ole Miss.
Use the following pieces of retrieved context to answer the question. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Keep the answer concise and professional.
Use the context to explain prerequisites or policies if asked.

Context:
{context}

Question: {question}

Answer:"""
        self.prompt = ChatPromptTemplate.from_template(self.template)

    async def get_answer(self, question: str) -> str:
        # Build Chain
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        rag_chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

        return await rag_chain.ainvoke(question)

rag_service = RAGService()
