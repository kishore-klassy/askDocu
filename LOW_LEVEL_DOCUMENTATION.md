# Low Level Documentation (LLD) - AI Helpdesk Assistant

## 1. System Overview

The AI Helpdesk Assistant is a Python-based application that crawls help websites, indexes their content using vector embeddings, and provides intelligent question-answering capabilities through both a Streamlit web interface and a command-line interface.

### 1.1 Architecture Pattern
- **Pattern**: Modular Service-Oriented Architecture
- **Framework**: Streamlit for web UI, Command-line for CLI
- **AI Model**: Hugging Face Mixtral-8x7B-Instruct-v0.1 via Inference API
- **Vector Search**: FAISS (Facebook AI Similarity Search)
- **Embedding Model**: SentenceTransformers all-MiniLM-L6-v2

## 2. Component Architecture

### 2.1 Core Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web UI        │    │   CLI Interface │    │   Core Modules  │
│ (chatbot_app.py)│    │  (qa_agent.py)  │    │   (modules/)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────────────────────────────────────┐
         │              Shared Components                  │
         ├─────────────────┬─────────────────┬─────────────┤
         │    Crawler      │  Vector Store   │  QA Engine  │
         │  (crawler.py)   │(vector_store.py)│(qa_engine.py)│
         └─────────────────┴─────────────────┴─────────────┘
```

### 2.2 Data Flow Architecture

```
[Help Website] → [Crawler] → [Documents] → [Vector Store] → [QA Engine] → [User Interface]
      ↓              ↓           ↓             ↓              ↓             ↓
   Web Content → BeautifulSoup → Text Docs → FAISS Index → LLM Query → Streamlit/CLI
```

## 3. Detailed Component Specifications

### 3.1 Web Crawler Module (`modules/crawler.py`)

**Purpose**: Crawls help websites and extracts textual content for indexing.

**Key Functions**:
- `crawl_help_site(base_url, max_pages=200)`: Main crawling function
- `extract_main_content(soup)`: Content extraction and cleaning
- `same_domain(base_url, test_url)`: Domain validation

**Algorithm**:
1. **BFS Traversal**: Uses breadth-first search with deque for URL queue
2. **Content Filtering**: Removes scripts, styles, navigation elements
3. **Domain Restriction**: Only crawls URLs within the same domain
4. **Rate Limiting**: Processes maximum 200 pages per crawl session

**Input**: Base URL string
**Output**: List of document dictionaries with `url` and `text` fields

**Error Handling**:
- HTTP timeout: 10 seconds per request
- Content-Type validation: Only processes HTML content
- Exception catching: Continues crawling on individual page failures

### 3.2 Vector Store Module (`modules/vector_store.py`)

**Purpose**: Manages document embeddings and similarity search using FAISS.

**Class: VectorStore**

**Initialization**:
- Model: `SentenceTransformer('all-MiniLM-L6-v2')`
- Index: FAISS IndexFlatL2 (L2 distance metric)
- Storage: Persistent storage in `data/` directory

**Key Methods**:

1. `build_index(documents)`:
   - Encodes documents into 384-dimensional embeddings
   - Creates FAISS index with L2 distance
   - Persists index and documents to disk

2. `load_index()`:
   - Loads pre-existing index from disk
   - Returns boolean success status

3. `query(query_text, top_k=5)`:
   - Encodes query into embedding space
   - Performs similarity search
   - Returns top-k most relevant documents

**Storage Files**:
- `data/vector.index`: FAISS index binary file
- `data/docs.npy`: NumPy serialized document array

**Performance Characteristics**:
- Embedding Dimension: 384
- Search Complexity: O(n) for IndexFlatL2
- Memory Usage: ~1.5KB per document + embeddings

### 3.3 QA Engine Module (`modules/qa_engine.py`)

**Purpose**: Orchestrates question-answering using retrieved context and LLM inference.

**Class: QAEngine**

**Initialization**:
- Vector Store: Injected dependency
- API: Hugging Face Inference API
- Model: `mistralai/Mixtral-8x7B-Instruct-v0.1`
- Authentication: HF_API_TOKEN environment variable

**Method: `answer_question(question)`**

**Algorithm**:
1. **Context Retrieval**: Query vector store for top-3 relevant documents
2. **Prompt Construction**: Build context-aware prompt with retrieved documents
3. **LLM Inference**: Send prompt to Mixtral model via HF API
4. **Response Processing**: Extract answer from generated text
5. **Source Attribution**: Return relevant document URLs

**Prompt Template**:
```
Answer the question based on the following documentation context. 
If the answer is not contained in the context, say you don't know.

Context:
{retrieved_documents}

Question: {user_question}
Answer:
```

**Parameters**:
- `max_new_tokens`: 256
- `temperature`: 0.2 (low for factual responses)

**Error Handling**:
- API failures: Returns error message
- Empty context: Returns "couldn't find information" message
- Unknown answers: Detects and handles "I don't know" responses

### 3.4 Streamlit Web Interface (`chatbot_app.py`)

**Purpose**: Provides interactive web-based chat interface.

**Session State Management**:
- `messages`: Conversation history array
- `qa_engine`: Initialized QA engine instance
- `help_url`: Currently configured help website URL

**UI Components**:

1. **Sidebar Configuration**:
   - URL input field
   - Crawl initiation button
   - Status feedback

2. **Main Chat Interface**:
   - Message input field
   - Send button
   - Chat history display with avatars

**Workflow**:
1. User enters help website URL
2. System crawls and indexes content (with loading spinner)
3. User asks questions in chat interface
4. System retrieves context and generates answers
5. Responses include source attribution with clickable links

**Message Format**:
```python
{
    "role": "user" | "bot",
    "text": "message_content"
}
```

### 3.5 Command Line Interface (`qa_agent.py`)

**Purpose**: Provides terminal-based question-answering interface.

**Usage**: `python qa_agent.py --url <help_website_url>`

**Workflow**:
1. Parse command-line arguments
2. Crawl specified help website
3. Build vector index
4. Enter interactive question loop
5. Exit on 'exit' or 'quit' commands

**Output Format**:
- Answer text
- Source URLs (if available)
- Session separator line

## 4. Data Structures

### 4.1 Document Structure
```python
{
    "url": str,      # Source webpage URL
    "text": str      # Extracted textual content
}
```

### 4.2 Vector Store Schema
- **Index**: FAISS IndexFlatL2 with 384-dimensional embeddings
- **Documents**: NumPy object array with document metadata
- **Persistence**: Binary files in `data/` directory

### 4.3 Message Schema (Streamlit)
```python
{
    "role": str,     # "user" or "bot"
    "text": str      # Message content with optional markdown
}
```

## 5. External Dependencies

### 5.1 Core Dependencies
- **requests**: HTTP client for web crawling and API calls
- **beautifulsoup4**: HTML parsing and content extraction
- **faiss-cpu**: Vector similarity search
- **sentence-transformers**: Document embedding generation
- **streamlit**: Web application framework
- **numpy**: Numerical operations and data serialization

### 5.2 AI/ML Dependencies
- **transformers**: Hugging Face model integration
- **accelerate**: Model acceleration utilities
- **huggingface-hub**: Model hub integration

### 5.3 UI Dependencies
- **streamlit-chat**: Enhanced chat UI components
- **pillow**: Image processing support

## 6. Configuration

### 6.1 Environment Variables
- `HF_API_TOKEN`: Hugging Face API token for model access

### 6.2 Hardcoded Configuration
- **Max Pages**: 200 pages per crawl session
- **HTTP Timeout**: 10 seconds per request
- **Embedding Model**: `all-MiniLM-L6-v2`
- **LLM Model**: `mistralai/Mixtral-8x7B-Instruct-v0.1`
- **Top-K Retrieval**: 3 documents for context
- **Max Tokens**: 256 for generated responses
- **Temperature**: 0.2 for consistent factual responses

## 7. File System Structure

```
/workspace/
├── chatbot_app.py          # Streamlit web interface
├── qa_agent.py             # Command-line interface
├── requirements.txt        # Python dependencies
├── modules/
│   ├── __init__.py        # Package initialization
│   ├── crawler.py         # Web crawling functionality
│   ├── vector_store.py    # Document indexing and retrieval
│   └── qa_engine.py       # Question-answering logic
└── data/
    ├── vector.index       # FAISS vector index (binary)
    └── docs.npy          # Document metadata (NumPy array)
```

## 8. Operational Workflows

### 8.1 Initialization Workflow
1. User provides help website URL
2. Crawler performs BFS traversal of website
3. Content extraction removes non-textual elements
4. Documents encoded into 384-dimensional embeddings
5. FAISS index created for similarity search
6. QA engine initialized with vector store

### 8.2 Question-Answering Workflow
1. User submits question
2. Question encoded into embedding space
3. Vector similarity search retrieves top-3 documents
4. Context and question formatted into LLM prompt
5. Mixtral model generates response via HF API
6. Answer extracted and sources attributed
7. Response displayed to user

### 8.3 Error Recovery
- **Network Failures**: Individual page failures don't stop crawling
- **API Errors**: Graceful degradation with error messages
- **Empty Results**: Fallback messages when no content found
- **Invalid URLs**: Input validation and user feedback

## 9. Performance Characteristics

### 9.1 Scalability Limits
- **Document Limit**: ~200 pages per crawl (configurable)
- **Memory Usage**: Linear with number of documents
- **Search Latency**: O(n) with current FAISS configuration
- **API Rate Limits**: Subject to Hugging Face inference API limits

### 9.2 Optimization Opportunities
- **Index Type**: Could use IndexIVFFlat for larger datasets
- **Caching**: No current caching of API responses
- **Parallel Processing**: Sequential document processing
- **Incremental Updates**: Full re-indexing on each crawl

## 10. Security Considerations

### 10.1 Input Validation
- Domain restriction prevents crawling external sites
- HTTP timeout prevents hanging requests
- Content-type validation ensures HTML processing only

### 10.2 API Security
- API token stored in environment variables
- HTTPS communication with Hugging Face API
- No sensitive data logging

### 10.3 Data Privacy
- No persistent user data storage
- Session-based conversation history
- Local vector storage only

## 11. Deployment Requirements

### 11.1 Environment Setup
1. Python 3.8+ runtime
2. Install dependencies: `pip install -r requirements.txt`
3. Set `HF_API_TOKEN` environment variable
4. Ensure `data/` directory exists and is writable

### 11.2 Execution Modes
- **Web Interface**: `streamlit run chatbot_app.py`
- **CLI Interface**: `python qa_agent.py --url <help_url>`

### 11.3 Resource Requirements
- **Memory**: ~2GB for typical document collections
- **Storage**: Variable based on crawled content size
- **Network**: Internet access for crawling and API calls

## 12. Monitoring and Debugging

### 12.1 Logging Points
- Crawl progress: Page count and URL processing
- Index building: Document count and embedding progress
- API calls: Request/response status
- Error conditions: Exception details and context

### 12.2 Debug Information
- Vector store statistics: Document count, embedding dimensions
- Search results: Relevance scores and source attribution
- Session state: Conversation history and engine status

## 13. Future Enhancement Areas

### 13.1 Performance Improvements
- Implement approximate nearest neighbor search (IndexIVFFlat)
- Add response caching layer
- Parallel document processing
- Incremental index updates

### 13.2 Feature Extensions
- Multi-language support
- Document type filtering (PDF, DOC support)
- Advanced search operators
- Conversation context awareness
- User feedback integration

### 13.3 Infrastructure Enhancements
- Containerization (Docker)
- Database integration for persistence
- Authentication and user management
- API rate limiting and quotas
- Monitoring and analytics dashboard

---

**Document Version**: 1.0  
**Last Updated**: $(date)  
**Maintainer**: Development Team  
**Review Cycle**: Quarterly