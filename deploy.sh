#!/bin/bash

# Production Deployment Script
# Run this to commit and prepare for deployment

echo "🚀 Preparing Build vs Buy Dashboard for Production Deployment..."

# Add all files
git add .

# Commit with deployment message
git commit -m "Production-ready: Clean deployment configuration

- Organized all deployment files in build_buy_app directory
- Removed duplicate requirements.txt files
- Updated deployment paths for cleaner structure
- All tests passing
- Ready for immediate deployment"

# Push to GitHub
git push origin main

echo ""
echo "✅ Code pushed to GitHub!"
echo ""
echo "🎯 Next Steps for Deployment:"
echo "1. Go to render.com"
echo "2. Sign up with GitHub"
echo "3. Click 'New +' → 'Web Service'"
echo "4. Connect 'Build-Buy-Dash' repository"
echo "5. Set source directory to 'build_buy_app'"
echo "6. Click 'Create Web Service'"
echo ""
echo "🌐 Your app will be live in 5-10 minutes!"
echo "📖 See DEPLOYMENT_READY.md for full instructions"
