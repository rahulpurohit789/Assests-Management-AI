# 🤖 AI Asset Management Chatbot

A powerful Streamlit application that provides intelligent querying of asset data using natural language. Built with LangChain, HuggingFace embeddings, and OpenAI.

## ✨ Features

- **🧠 Natural Language Understanding**: Ask questions in plain English
- **🔍 Vector-Based Search**: Semantic search using HuggingFace embeddings
- **🤖 AI-Generated Responses**: Intelligent explanations, not just raw data
- **📊 Real-Time Analysis**: Live asset data insights
- **🎯 Source Attribution**: See which assets the AI used for responses
- **⚡ Fast Performance**: Cached vector database for quick responses

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment
Create a `.env` file in the project root:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run the Application
```bash
streamlit run app.py
```

## 📁 Project Structure

```
AI-Asset-Chatbot/
├── app.py                 # Main application entry point
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── README.md             # This file
├── JsonData/
│   └── Data.json         # Your asset data
├── src/
│   ├── __init__.py
│   ├── config.py         # Configuration management
│   ├── data_loader.py    # Data loading and processing
│   ├── ai_components.py  # AI/ML components
│   └── ui_components.py  # UI components
└── faiss_index/          # Cached vector database (auto-created)
```

## 🔧 Configuration

### Environment Variables
- `GROQ_API_KEY`: Your Groq API key (required)

### Model Settings
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **LLM Model**: `meta-llama/llama-4-scout-17b-16e-instruct`
- **Vector Store**: FAISS with 5 document retrieval

## 💬 Example Queries

Try these natural language queries:

- "Show me all assets from Singapore"
- "List all Caterpillar machines"
- "Which vehicles are assigned to Homer Simpson?"
- "What is the warranty expiration date for MPT-001?"
- "How many assets are in each category?"
- "Tell me about the most expensive assets"

## 🛠️ Technical Stack

- **Frontend**: Streamlit
- **AI Framework**: LangChain
- **Embeddings**: HuggingFace Transformers
- **Vector Store**: FAISS
- **LLM**: OpenAI Chat models
- **Data**: JSON

## 📊 Data Format

The application expects a JSON file with an array of asset objects:

```json
[
  {
    "assetId": "MPT-001",
    "entityName": "SINGAPORE",
    "description": "2019 Dodge Ram 3500",
    "manufacturer": "Dodge",
    "model": "Ram 3500",
    "categoryId": "Truck",
    "typeId": "Pickup",
    "statusId": "ACTIVE",
    "customer": "Simpson, Homer",
    "purchaseDate": "2012-04-09T00:00:00",
    "purchaseCost": 45000,
    "customFields": [
      {
        "fieldName": "WARRANTY EXPIRATION",
        "value": "2015-10-31T00:00:00.000"
      }
    ]
  }
]
```

## 🔑 Getting Your OpenAI API Key

1. Visit [platform.openai.com](https://platform.openai.com)
2. Sign up or log in, then create an API key
3. Go to "API Keys" section
4. Create a new API key
5. Copy the key and add it to your `.env` file

## 🚀 Deployment

### Streamlit Cloud
1. Push your code to GitHub
2. Connect to [share.streamlit.io](https://share.streamlit.io)
3. Set `GROQ_API_KEY` in secrets
4. Deploy!

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable
export GROQ_API_KEY="your-key-here"

# Run the app
streamlit run app.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🆘 Support

If you encounter any issues:
1. Check that your `.env` file has the correct `GROQ_API_KEY`
2. Ensure your JSON data file is in the correct format
3. Verify all dependencies are installed correctly

---

**Built with ❤️ using Streamlit, LangChain, and AI**