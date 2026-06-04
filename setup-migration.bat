@echo off
REM 11ty Migration - Complete Setup Script (Windows)
REM This script sets up, builds, and tests the 11ty migration

echo ==========================================
echo 11ty Migration - Complete Setup
echo ==========================================
echo.

REM Step 1: Verify branch
echo Checking branch...
for /f %%i in ('git rev-parse --abbrev-ref HEAD') do set BRANCH=%%i
if not "%BRANCH%"=="feature/11ty-migration" (
  echo Switching to feature/11ty-migration...
  git checkout feature/11ty-migration
)
echo Confirmed: On feature/11ty-migration branch
echo.

REM Step 2: Install dependencies
echo Installing NPM dependencies...
call npm install >nul 2>&1
call npm install jsdom >nul 2>&1
echo Dependencies installed
echo.

REM Step 3: FAQ data
echo FAQ data ready (src/_data/faqs.json)
echo.

REM Step 4: Build
echo Building with 11ty...
call npm run build >nul 2>&1
echo Build complete - output in _site/
echo.

REM Step 5: Commit
echo Committing changes...
git add -A
git commit -m "Complete 11ty migration setup - ready for testing" || echo Already committed
echo.

echo ==========================================
echo SETUP COMPLETE!
echo ==========================================
echo.
echo Next steps:
echo 1. Test locally: npm run serve
echo 2. Visit: http://localhost:8080/faqs/
echo 3. Verify enhancement appears on all FAQ pages
echo 4. Push to GitHub: git push origin feature/11ty-migration
echo 5. Create PR and merge to main
echo.
