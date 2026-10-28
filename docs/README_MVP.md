# AI Assistant MVP

Welcome to the Personal AI Assistant MVP! This project implements a full-stack RAG (Retrieval-Augmented Generation) system that allows you to chat with your own documents.

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone <repository-url>
cd usecase
```

### 2. Run the Demo (Docker)
The fastest way to get started is with Docker Compose. This will spin up the frontend, backend, database, and vector store.

```bash
docker compose -f infra/docker-compose.yml up --build
```

### 3. Access the App
- **Frontend**: Open [http://localhost:5173](http://localhost:5173) in your browser.
- **API Documentation**: Visit [http://localhost:8000/docs](http://localhost:8000/docs) to explore the FastAPI Swagger UI.

## 🛠️ How it Works

1. **Knowledge Base**: Documents are embedded using `sentence-transformers` and stored in **Milvus**.
2. **Retrieval**: When you ask a question, the system finds the most relevant document chunks.
3. **Generation**: The chunks are passed to an **LLM** (Local Llama, TGI, or Groq) to generate a grounded response.

## 📖 User Guide

### Creating an Account
1. Navigate to the sign-up page on the frontend.
2. Create a user with an email and password.
3. Log in to start a chat session.

### Chatting with AI
- Type your query in the chat box.
- The AI will use the retrieved context to answer your questions accurately.

## ⚙️ Configuration

You can customize the system by editing the `.env` file or passing environment variables to Docker:

| Variable | Description | Default |
|-----------|-------------|---------|
| `LLM_MODE` | LLM backend (`local_llama`, `http_tgi`, `groq`) | `http_tgi` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://...` |
| `MILVUS_URI` | Milvus server address | `http://localhost:19530` |

## 🤝 Contributing

Please refer to the [Developer Guide](docs/dev-guide.md) for instructions on how to set up your environment and add new features.
