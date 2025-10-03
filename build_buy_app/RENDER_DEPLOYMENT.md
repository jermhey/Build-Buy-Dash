# Render Deployment Guide - Build vs Buy Dashboard

## ✅ 100% Render Compatible

This application is **fully compatible** with Render's free tier and production hosting.

## Quick Deploy to Render

### Method 1: Automatic (Using render.yaml)

1. **Push to GitHub:**
   ```bash
   git push origin main
   ```

2. **Connect to Render:**
   - Go to [dashboard.render.com](https://dashboard.render.com)
   - Click "New +" → "Blueprint"
   - Select your `Build-Buy-Dash` repository
   - Render will auto-detect `render.yaml` and configure everything

3. **Deploy:**
   - Click "Apply"
   - Wait 2-3 minutes
   - Your app is live! 🎉

### Method 2: Manual Configuration

1. **Go to Render Dashboard:**
   - [dashboard.render.com](https://dashboard.render.com)
   - Click "New +" → "Web Service"

2. **Configure Settings:**

   | Setting | Value |
   |---------|-------|
   | **Repository** | Your GitHub repo URL |
   | **Branch** | `main` |
   | **Root Directory** | `build_buy_app` ⚠️ **CRITICAL** |
   | **Environment** | `Python 3` |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `gunicorn app:server --bind 0.0.0.0:$PORT --workers 1 --timeout 30` |
   | **Plan** | `Free` or `Starter` |

3. **Environment Variables** (Auto-set by Render):
   - `PORT` - Render sets this automatically
   - No other variables needed!

4. **Click "Create Web Service"**

## Render Compatibility Checklist

### ✅ Requirements Met

- [x] **Gunicorn Server**: `gunicorn==21.2.0` installed
- [x] **WSGI Application**: `server` object exposed at module level
- [x] **Port Binding**: Automatically binds to `$PORT` environment variable
- [x] **Python Version**: 3.11.5 specified in `runtime.txt`
- [x] **Dependencies**: All pinned in `requirements.txt`
- [x] **Build Command**: Standard pip install
- [x] **No Database**: Stateless application (scenarios stored in filesystem)
- [x] **Auto-scaling**: Works with Render's auto-scaling
- [x] **Health Checks**: Responds to HTTP requests on root path

### ✅ Deployment Files Present

1. **render.yaml** - Blueprint configuration (automatic deployment)
2. **requirements.txt** - Python dependencies
3. **runtime.txt** - Python version (3.11.5)
4. **Procfile** - Alternative for Heroku/Railway (not used by Render)
5. **start.sh** - Alternative startup script (not used when using render.yaml)

### ✅ Application Structure

```
build_buy_app/                 ← Set as Root Directory in Render
├── app.py                     ← Main application (exports 'server')
├── requirements.txt           ← Dependencies
├── runtime.txt               ← Python version
├── render.yaml               ← Render configuration
├── Procfile                  ← Backup for other platforms
├── start.sh                  ← Backup startup script
├── config/                   ← Configuration modules
├── core/                     ← Business logic
├── data/                     ← Data management
├── src/                      ← Simulation engine
├── ui/                       ← User interface
└── tests/                    ← Test suite
```

## Production Features

### Automatic Environment Detection

The app automatically detects Render's production environment:

```python
# In config/security.py
is_production = os.environ.get('PORT') is not None
```

When `PORT` is set (by Render), the app:
- ✅ Enables security headers (CSP, HSTS, X-Frame-Options, etc.)
- ✅ Disables debug mode
- ✅ Optimizes error handling
- ✅ Applies strict session security
- ✅ Uses production-grade logging

### Security (Production-Ready)

- **HTTPS**: Render provides free SSL certificates
- **Security Headers**: Auto-enabled in production
- **Session Security**: Strict SameSite cookies, HTTPOnly
- **Input Validation**: All user inputs sanitized
- **Path Traversal Protection**: UUID validation for file operations
- **No Secrets in Code**: All sensitive data via environment variables

## Render-Specific Configuration

### Current render.yaml Configuration:

```yaml
services:
  - type: web
    name: build-buy-dashboard
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: "gunicorn app:server --bind 0.0.0.0:$PORT --workers 1 --timeout 30"
    envVars:
      - key: PORT
        value: 8080        # Render overrides this
      - key: PYTHONPATH
        value: /opt/render/project/src
```

### Why This Works:

1. **`app:server`**: Points to the module-level `server` object in `app.py`
2. **`--bind 0.0.0.0:$PORT`**: Binds to Render's dynamic port
3. **`--workers 1`**: Optimized for Render's free tier (512MB RAM)
4. **`--timeout 30`**: Allows time for Excel generation

## Verification Steps

After deployment, verify:

1. **Visit your app URL**: `https://your-app-name.onrender.com`
2. **Test functionality**:
   - Dashboard loads ✅
   - Can input parameters ✅
   - Simulation runs ✅
   - Excel export downloads ✅
3. **Check security headers** (Browser DevTools → Network):
   - `X-Frame-Options: DENY` ✅
   - `Content-Security-Policy` present ✅
   - `Strict-Transport-Security` present ✅

## Troubleshooting

### Build Fails

**Issue**: "No module named 'dash'"
- **Fix**: Ensure Root Directory is set to `build_buy_app`

**Issue**: "Could not find a version that satisfies..."
- **Fix**: Check `requirements.txt` has correct versions
- **Verify**: `werkzeug>=3.0.0,<3.1` (compatible with Dash 2.18.1)

### App Crashes on Start

**Issue**: "Address already in use"
- **Fix**: This shouldn't happen on Render (port is dynamic)
- **Verify**: Start command uses `$PORT` variable

**Issue**: "Module not found"
- **Fix**: Verify Root Directory is `build_buy_app`
- **Check**: All imports use relative paths

### Slow Initial Load

**Expected**: First request after idle takes ~30 seconds (free tier sleeps)
- **Solution**: Upgrade to Starter plan for always-on
- **Workaround**: Set up a ping service (uptime robot)

## Performance Optimization for Render

### Free Tier (512MB RAM)

Current configuration is optimized:
- ✅ 1 Gunicorn worker (low memory footprint)
- ✅ Efficient Excel generation (streaming)
- ✅ No large in-memory datasets
- ✅ Stateless architecture

### Starter Tier (2GB RAM)

For better performance, can increase workers:
```yaml
startCommand: "gunicorn app:server --bind 0.0.0.0:$PORT --workers 2 --timeout 60"
```

## Render vs Other Platforms

| Feature | Render | Railway | Heroku |
|---------|--------|---------|--------|
| Free Tier | ✅ Yes | ✅ Yes | ❌ No |
| Auto-Deploy | ✅ Yes | ✅ Yes | ✅ Yes |
| Custom Domain | ✅ Yes | ✅ Yes | ✅ Yes |
| SSL Certificate | ✅ Free | ✅ Free | ✅ Free |
| Sleep on Idle | ✅ Yes | ❌ No | ✅ Yes |
| Build Time | ~2-3 min | ~1-2 min | ~3-5 min |

## Next Steps After Deployment

1. **Custom Domain** (Optional):
   - Go to your service → Settings → Custom Domain
   - Add your domain and configure DNS

2. **Environment Variables** (If needed):
   - Settings → Environment → Add variable
   - Example: `SECRET_KEY` for enhanced session security

3. **Monitoring**:
   - Render provides basic metrics
   - Add external monitoring (UptimeRobot, etc.)

4. **Backups**:
   - Scenarios are stored in filesystem
   - Consider adding cloud storage (S3) for persistence

## Support

- **Render Docs**: [render.com/docs](https://render.com/docs)
- **This App's Docs**: See `README.md` and `SECURITY.md`
- **Issues**: GitHub issues for app-specific problems

---

## Summary

**This application is 100% compatible with Render** and follows all best practices:

✅ Correct file structure
✅ Proper WSGI server configuration  
✅ Environment variable detection
✅ Production security features
✅ Optimized for free tier
✅ Auto-deploy ready
✅ No manual configuration needed (with render.yaml)

**Deploy with confidence!** 🚀

