#!/usr/bin/env python3
"""
Test script to verify GitHub Actions setup locally
"""
import os
import sys
import json

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} missing: {filepath}")
        return False

def check_env_var(var_name, description):
    """Check if environment variable is set"""
    value = os.environ.get(var_name)
    if value:
        print(f"✅ {description}: {var_name} = {value[:10]}{'...' if len(value) > 10 else ''}")
        return True
    else:
        print(f"⚠️  {description} not set: {var_name}")
        return False

def main():
    print("="*60)
    print("🔍 GitHub Actions Setup Checker")
    print("="*60)
    print()
    
    checks_passed = 0
    checks_failed = 0
    
    print("📁 Checking required files...")
    print("-" * 60)
    
    files_to_check = [
        ("full_workflow.py", "Main scraper script"),
        (".github/workflows/scraper.yml", "GitHub Actions workflow"),
        ("send_results.py", "Result sender script"),
        ("requirements.txt", "Python dependencies"),
        (".gitignore", "Git ignore file"),
    ]
    
    for filepath, description in files_to_check:
        if check_file_exists(filepath, description):
            checks_passed += 1
        else:
            checks_failed += 1
    
    print()
    print("🔑 Checking environment variables (for local testing)...")
    print("-" * 60)
    
    env_vars = [
        ("LOGIN_EMAIL", "Login email"),
        ("LOGIN_PASSWORD", "Login password"),
        ("N8N_WEBHOOK_URL", "n8n webhook URL"),
    ]
    
    for var_name, description in env_vars:
        if check_env_var(var_name, description):
            checks_passed += 1
        # Don't count as failed - these are only needed on GitHub
    
    print()
    print("📦 Checking Python dependencies...")
    print("-" * 60)
    
    try:
        import selenium
        print(f"✅ Selenium installed: {selenium.__version__}")
        checks_passed += 1
    except ImportError:
        print("❌ Selenium not installed")
        checks_failed += 1
    
    try:
        import requests
        print(f"✅ Requests installed: {requests.__version__}")
        checks_passed += 1
    except ImportError:
        print("❌ Requests not installed")
        checks_failed += 1
    
    print()
    print("🌐 Checking Git configuration...")
    print("-" * 60)
    
    if os.path.exists('.git'):
        print("✅ Git repository initialized")
        checks_passed += 1
        
        # Check remote
        try:
            import subprocess
            result = subprocess.run(['git', 'remote', '-v'], 
                                  capture_output=True, text=True)
            if 'origin' in result.stdout:
                print("✅ Git remote 'origin' configured")
                print(f"   {result.stdout.split()[1]}")
                checks_passed += 1
            else:
                print("⚠️  Git remote 'origin' not configured")
                print("   Run: git remote add origin <your-repo-url>")
        except Exception as e:
            print(f"⚠️  Could not check git remote: {e}")
    else:
        print("❌ Git repository not initialized")
        print("   Run: git init")
        checks_failed += 1
    
    print()
    print("📋 Checking workflow file syntax...")
    print("-" * 60)
    
    if os.path.exists('.github/workflows/scraper.yml'):
        try:
            import yaml
            with open('.github/workflows/scraper.yml', 'r') as f:
                yaml.safe_load(f)
            print("✅ Workflow YAML syntax valid")
            checks_passed += 1
        except ImportError:
            print("⚠️  PyYAML not installed, skipping YAML validation")
            print("   Install with: pip install pyyaml")
        except Exception as e:
            print(f"❌ Workflow YAML syntax error: {e}")
            checks_failed += 1
    
    print()
    print("="*60)
    print("📊 Summary")
    print("="*60)
    print(f"✅ Passed: {checks_passed}")
    print(f"❌ Failed: {checks_failed}")
    print()
    
    if checks_failed == 0:
        print("🎉 All checks passed! You're ready to push to GitHub.")
        print()
        print("Next steps:")
        print("1. Push code: git push origin main")
        print("2. Set GitHub Secrets (LOGIN_EMAIL, LOGIN_PASSWORD, N8N_WEBHOOK_URL)")
        print("3. Create GitHub Personal Access Token")
        print("4. Configure n8n workflow")
        print("5. Test the workflow!")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("   See COMPLETE_SETUP_GUIDE.md for help.")
    
    print("="*60)
    
    return 0 if checks_failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
