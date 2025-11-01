# Render Deployment Guide for Backend

This guide will walk you through deploying your Flask backend to Render.

## Prerequisites

1. **GitHub Account**: Your code should be in a GitHub repository
2. **Render Account**: Sign up at [render.com](https://render.com) (free tier available)
3. **Gemini API Key** (optional): If you want to use Gemini AI features

## Step-by-Step Deployment

### Step 1: Prepare Your Repository

Ensure your backend code is pushed to GitHub. The `backend/` directory should contain:
- ✅ `app.py` (main Flask application)
- ✅ `requirements.txt` (Python dependencies)
- ✅ `Procfile` (Gunicorn configuration)
- ✅ `runtime.txt` (Python version - **REQUIRED** to fix scikit-learn build issues)
- ✅ `gemini_service.py` (if using Gemini)
- ✅ Other necessary files (models, data, etc.)

**Important**: Make sure `backend/runtime.txt` contains `python-3.11.10` and is committed to your repository before deploying!

### Step 2: Create a Render Account

1. Go to [render.com](https://render.com)
2. Sign up or log in with your GitHub account
3. Connect your GitHub account if prompted

### Step 3: Create a New Web Service

1. From the Render dashboard, click **"New +"** button
2. Select **"Web Service"**
3. Connect your GitHub repository:
   - If not connected, click "Configure account" to connect GitHub
   - Select your repository from the list
   - Click "Connect"

### Step 4: Configure the Web Service

Fill in the following settings:

#### Basic Settings
- **Name**: `ai-recruitment-backend` (or your preferred name)
- **Region**: Choose closest to your users (e.g., `Oregon (US West)`)
- **Branch**: `main` (or your default branch)
- **Root Directory**: `backend` ⚠️ **Important!**

#### Build & Deploy Settings
- **Runtime**: `Python 3` 
- **Python Version**: **MUST BE SET TO `3.11.10`** ⚠️ **CRITICAL!**
  - In the Render dashboard, look for "Python Version" dropdown
  - Select `3.11.10` (NOT 3.13.x - scikit-learn doesn't support it)
  - If you don't see this option, go to **"Advanced"** settings
- **Build Command**: 
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```bash
  gunicorn app:app --bind 0.0.0.0:$PORT --workers 4
  ```
  Or simply: `gunicorn app:app` (Render auto-sets PORT)

⚠️ **CRITICAL**: You MUST manually set Python Version to `3.11.10` in Render dashboard. The `runtime.txt` file helps, but the dashboard setting takes precedence. Without this, you'll get scikit-learn compilation errors!

#### Environment Variables

Click **"Advanced"** → **"Add Environment Variable"** and add:

1. **PORT** (optional - Render sets this automatically)
   - Value: Leave empty or `$PORT`

2. **GEMINI_API_KEY** (if using Gemini AI)
   - Key: `GEMINI_API_KEY`
   - Value: Your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - ⚠️ **Important**: Keep this secret!

3. **FLASK_ENV** (optional)
   - Key: `FLASK_ENV`
   - Value: `production`

4. **PYTHON_VERSION** (optional)
   - Key: `PYTHON_VERSION`
   - Value: `3.11` or `3.10`

### Step 5: Deploy

1. Review all settings
2. Click **"Create Web Service"**
3. Render will start building and deploying your service
4. Monitor the build logs in real-time

### Step 6: Verify Deployment

1. Wait for deployment to complete (usually 2-5 minutes)
2. Once deployed, you'll see a URL like: `https://ai-recruitment-backend.onrender.com`
3. Test the health endpoint: `https://your-app-name.onrender.com/api/health`
4. You should see:
   ```json
   {
     "status": "healthy",
     "message": "AI Recruitment System API is running",
     "gemini_available": true/false
   }
   ```

## Configuration Details

### Procfile
Your `Procfile` should contain:
```
web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 4
```

### requirements.txt
Ensure these are included:
```
flask==2.3.3
flask-cors==4.0.0
gunicorn==21.2.0
google-generativeai==0.3.2  # if using Gemini
# ... other dependencies
```

### Important Notes

1. **Root Directory**: Must be set to `backend` since your Flask app is in a subdirectory
2. **PORT**: Render automatically provides the `$PORT` environment variable
3. **File Uploads**: The `uploads/` directory is ephemeral on Render. For production, consider:
   - Using AWS S3, Google Cloud Storage, or similar
   - Or using Render Disk (paid feature)
4. **Free Tier Limitations**:
   - Services spin down after 15 minutes of inactivity
   - First request after spin-down takes ~30 seconds
   - Consider upgrading for always-on service

## Updating Your Frontend

After deploying to Render, update your frontend to use the new backend URL:

### Option 1: Environment Variable (Recommended)

In your React app, update API calls to use:
```javascript
const API_URL = process.env.REACT_APP_API_URL || 'https://your-app-name.onrender.com';
```

Set `REACT_APP_API_URL` in your frontend deployment (Vercel/Netlify/etc.)

### Option 2: Update package.json

Change the proxy in `package.json`:
```json
{
  "proxy": "https://your-app-name.onrender.com"
}
```

## Troubleshooting

### Build Fails

#### Python Version / scikit-learn Compilation Errors
If you see Cython compilation errors with scikit-learn:
- ✅ **Solution**: Ensure `backend/runtime.txt` exists with `python-3.11.10`
- scikit-learn 1.3.2 doesn't support Python 3.13
- Render should automatically use Python 3.11 if `runtime.txt` is present

Other build issues:
- Check build logs for error messages
- Ensure `requirements.txt` has all dependencies
- Verify Python version compatibility (should be 3.11)
- Check that `backend/` is set as root directory

### App Crashes on Start
- Verify `Procfile` is correct
- Check that `app.py` exists in root directory
- Review logs for import errors
- Ensure all file paths are relative (not absolute)

### Health Check Fails
- Verify `/api/health` endpoint exists
- Check that app is binding to `0.0.0.0` and `$PORT`
- Review application logs

### Gemini Not Working
- Verify `GEMINI_API_KEY` environment variable is set
- Check API key is valid
- Review logs for authentication errors

### Slow First Request
- This is normal on free tier (cold starts)
- Service wakes up after ~30 seconds
- Consider upgrading to paid tier for always-on

## Environment Variables Summary

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Optional | Google Gemini API key |
| `FLASK_ENV` | Optional | Set to `production` |
| `PORT` | Auto-set | Render provides this automatically |

## Next Steps

1. ✅ Backend deployed to Render
2. Update frontend API URL
3. Test all endpoints
4. Set up monitoring/alerting (optional)
5. Configure custom domain (optional, paid feature)

## Useful Links

- [Render Documentation](https://render.com/docs)
- [Python on Render](https://render.com/docs/deploy-python)
- [Environment Variables](https://render.com/docs/environment-variables)
- [Health Checks](https://render.com/docs/healthchecks)

---

**Need Help?** Check Render's logs or create an issue in your repository.

