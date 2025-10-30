# 🚀 Streamlit Cloud Deployment Guide

This guide will help you deploy your AI Asset Management Chatbot to Streamlit Cloud.

## 📋 Pre-Deployment Checklist

- [x] Code structure fixed (ai_components.py)
- [x] Requirements.txt updated with specific versions
- [x] Streamlit configuration created
- [x] Environment variables template created
- [ ] Test application locally
- [ ] Push to GitHub repository
- [ ] Deploy to Streamlit Cloud

## 🔧 Local Testing

Before deploying, test your application locally:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file with your API key
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# 3. Run the application
streamlit run app.py
```

## 🌐 Streamlit Cloud Deployment

### Step 1: Prepare Your Repository

1. **Push to GitHub**: Make sure your code is in a GitHub repository
2. **Verify Structure**: Ensure all files are in the root directory:
   ```
   ├── app.py
   ├── requirements.txt
   ├── .streamlit/config.toml
   ├── .env.example
   ├── src/
   │   ├── __init__.py
   │   ├── config.py
   │   ├── data_loader.py
   │   ├── ai_components.py
   │   └── ui_components.py
   ├── JsonData/
   │   └── Data.json
   └── faiss_index/
       ├── index.faiss
       └── index.pkl
   ```

### Step 2: Deploy to Streamlit Cloud

1. **Go to [share.streamlit.io](https://share.streamlit.io)**
2. **Sign in** with your GitHub account
3. **Click "New app"**
4. **Fill in the details**:
   - **Repository**: Select your GitHub repository
   - **Branch**: `main` (or your default branch)
   - **Main file path**: `app.py`
   - **App URL**: Choose a unique name (e.g., `your-username-asset-chatbot`)

### Step 3: Configure Environment Variables

1. **In the Streamlit Cloud dashboard**, go to your app
2. **Click "Settings"** (gear icon)
3. **Go to "Secrets"** tab
4. **Add your environment variables**:
   ```toml
   OPENAI_API_KEY = "your_actual_openai_api_key_here"
   ```

### Step 4: Deploy

1. **Click "Deploy"**
2. **Wait for deployment** (usually 2-5 minutes)
3. **Check logs** if there are any issues

## 🔍 Troubleshooting

### Common Issues:

1. **Import Errors**: Make sure all dependencies are in requirements.txt
2. **API Key Issues**: Verify GROQ_API_KEY is set correctly in secrets
3. **File Not Found**: Ensure all files are in the correct directory structure
4. **Memory Issues**: Streamlit Cloud has memory limits; consider optimizing if needed

### Debug Steps:

1. **Check the logs** in Streamlit Cloud dashboard
2. **Test locally** with the same environment
3. **Verify file paths** are correct
4. **Check API key** is valid and has credits

## 📊 Performance Tips

- **FAISS Index**: The pre-built index will speed up initial load
- **Caching**: Streamlit's @st.cache_resource is used for optimal performance
- **Memory**: Monitor memory usage in the dashboard

## 🔒 Security Notes

- **Never commit** your `.env` file with real API keys
- **Use Streamlit secrets** for production environment variables
- **Keep your API keys secure** and rotate them regularly

## 📈 Monitoring

- **View logs** in the Streamlit Cloud dashboard
- **Monitor usage** and performance metrics
- **Check error logs** if the app stops working

## 🆘 Support

If you encounter issues:
1. Check the [Streamlit Cloud documentation](https://docs.streamlit.io/streamlit-community-cloud)
2. Review the logs in your Streamlit Cloud dashboard
3. Test locally to isolate the issue

---

**Your chatbot is now ready for deployment! 🎉**
