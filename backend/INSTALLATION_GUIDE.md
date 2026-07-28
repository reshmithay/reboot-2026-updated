# Installation Guide - Corporate Network

## Issue
Your corporate network is blocking PyPI package downloads. You're getting:
```
ERROR: 403 Client Error: Forbidden for url: https://files.pythonhosted.org/...
```

## Solution Options

### Option 1: Contact IT Support (Recommended)

Request access to install Python packages. Ask your IT team to:

1. **Allow access to PyPI**:
   - `pypi.org`
   - `files.pythonhosted.org`

2. **Or provide corporate PyPI proxy**:
   ```bash
   pip config set global.index-url <corporate-proxy-url>
   ```

3. **Or pre-install these packages**:
   ```
   fastapi==0.111.0
   uvicorn[standard]==0.30.1
   pydantic==2.7.4
   pydantic-settings==2.3.3
   google-cloud-bigquery==3.25.0
   pandas==2.2.0
   numpy==1.26.0
   scikit-learn==1.5.0
   ```

### Option 2: Manual Package Installation

If you have another machine with internet access:

1. **Download packages** on internet-connected machine:
   ```bash
   pip download -d packages fastapi uvicorn pydantic pydantic-settings
   ```

2. **Transfer the `packages` folder** to your corporate machine

3. **Install from local folder**:
   ```bash
   cd c:\Users\7316575\MaheshR\reboot-2026\blockchain-anomaly-ai\backend
   .\venv\Scripts\python.exe -m pip install --no-index --find-links=packages fastapi uvicorn pydantic pydantic-settings
   ```

### Option 3: Use Corporate Python Distribution

Check if your organization provides:
- **Anaconda Enterprise**
- **Internal PyPI mirror**
- **Pre-configured Python environment**

Contact your Python/Data Science support team.

### Option 4: Test Without Web Server

While waiting for package installation, you can still:

1. **Review the code** - All detection logic is implemented
2. **Run unit tests** - Once pytest is available
3. **Use the test script** - See `test_detection_standalone.py`

## Once Packages Are Installed

### Start the Backend Server

```bash
# Navigate to backend
cd c:\Users\7316575\MaheshR\reboot-2026\blockchain-anomaly-ai\backend

# Activate virtual environment
.\venv\Scripts\python.exe

# Run the server
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

### Test the API

```bash
# Health check
curl http://localhost:8000/health

# API documentation
# Open in browser: http://localhost:8000/docs
```

### Run Example Detection

```bash
.\venv\Scripts\python.exe app\services\anomaly\example_usage.py
```

## Environment Configuration

1. **Copy environment template**:
   ```bash
   copy .env.example .env
   ```

2. **Edit `.env` file** with your credentials:
   - `GOOGLE_APPLICATION_CREDENTIALS` - Path to GCP service account key
   - `BIGQUERY_PROJECT_ID` - Your GCP project ID
   - `GEMINI_API_KEY` - Your Gemini API key (if using LLM narratives)

## Troubleshooting

### Issue: "Cannot find module 'app'"
**Solution**: Make sure you're in the `backend` directory and PYTHONPATH is set:
```bash
$env:PYTHONPATH = "c:\Users\7316575\MaheshR\reboot-2026\blockchain-anomaly-ai\backend"
```

### Issue: "No module named 'google.cloud'"
**Solution**: Install Google Cloud dependencies:
```bash
.\venv\Scripts\python.exe -m pip install google-cloud-bigquery
```

### Issue: "Permission denied" when activating venv
**Solution**: Use direct Python path instead:
```bash
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

## Next Steps

1. ✅ Virtual environment created
2. ⏳ **Install packages** (waiting for network access)
3. ⏳ Configure `.env` file
4. ⏳ Start the server
5. ⏳ Test API endpoints

## Support

- **Internal IT Support**: For network/proxy issues
- **Project Documentation**: See `docs/DEVELOPMENT_SETUP.md`
- **Code Documentation**: See `docs/BEST_PRACTICES.md`
