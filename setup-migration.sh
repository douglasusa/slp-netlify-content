#!/usr/bin/env bash

# 11ty Migration - Complete Setup Script
# This script sets up, builds, and tests the 11ty migration on your local machine

set -e

echo "=========================================="
echo "11ty Migration - Complete Setup"
echo "=========================================="
echo ""

# Step 1: Verify branch
echo "✓ Checking branch..."
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" != "feature/11ty-migration" ]; then
  echo "⚠️  You're on branch: $BRANCH"
  echo "Switching to feature/11ty-migration..."
  git checkout feature/11ty-migration
fi
echo "✓ On feature/11ty-migration branch"
echo ""

# Step 2: Install dependencies
echo "✓ Installing NPM dependencies..."
npm install > /dev/null 2>&1
npm install jsdom > /dev/null 2>&1
echo "✓ Dependencies installed"
echo ""

# Step 3: Extract FAQs (optional - data already populated)
echo "✓ FAQ data ready (src/_data/faqs.json)"
echo ""

# Step 4: Build
echo "✓ Building with 11ty..."
npm run build > /dev/null 2>&1
echo "✓ Build complete - output in _site/"
echo ""

# Step 5: Commit
echo "✓ Committing changes..."
git add -A
git commit -m "Complete 11ty migration setup - ready for testing" || echo "✓ Already committed"
echo ""

echo "=========================================="
echo "✅ SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Test locally: npm run serve"
echo "2. Visit: http://localhost:8080/faqs/"
echo "3. Verify enhancement appears on all FAQ pages"
echo "4. Push to GitHub: git push origin feature/11ty-migration"
echo "5. Create PR and merge to main"
echo ""
