# Deployment Guide for URBAN-COOL AI

This guide details instructions for deploying the **URBAN-COOL AI** frontend to **Vercel** and the backend API to **Render**.

---

## 1. Frontend Deployment (Vercel)

### Step 1: Push Repository to GitHub
Ensure all Phase 0 files are committed to your GitHub repository.

### Step 2: Create New Project on Vercel
1. Log into your [Vercel Dashboard](https://vercel.com).
2. Click **Add New** -> **Project**.
3. Select your `urban-cool-ai` GitHub repository.
4. Set **Root Directory** to `frontend`.
5. Framework Preset will automatically detect **Next.js**.

### Step 3: Configure Environment Variables
In Vercel Project Settings -> Environment Variables, add:
- `NEXT_PUBLIC_API_URL`: `https://urban-cool-ai-backend.onrender.com` (Replace with your deployed Render backend API URL).

### Step 4: Deploy
Click **Deploy**. Vercel will build and deploy the Next.js frontend application.

---

## 2. Backend Deployment (Render)

### Option A: Automatic Blueprint Deployment (Recommended)
1. Log into your [Render Dashboard](https://render.com).
2. Click **Blueprints** -> **New Blueprint Instance**.
3. Connect your repository. Render will automatically detect `render.yaml` at the root of the project.
4. Render will create the `urban-cool-ai-backend` Python service.

### Option B: Manual Web Service Setup
1. On Render Dashboard, click **New +** -> **Web Service**.
2. Select repository.
3. Configure settings:
   - **Name**: `urban-cool-ai-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add Environment Variables:
   - `CORS_ORIGINS`: `https://urban-cool-ai.vercel.app`
   - `ENVIRONMENT`: `production`
   - `GEE_PROJECT_ID`: (Your Google Cloud Project ID for Phase 1)
   - `GEE_SERVICE_ACCOUNT`: (Your GEE Service Account)
   - `GEE_PRIVATE_KEY`: (Your GEE Private Key)

Click **Create Web Service**.
