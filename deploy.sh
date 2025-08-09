#!/bin/bash
# QuickAid Deployment Helper Script

echo "🚀 QuickAid Deployment Helper"
echo "=============================="

# Check git status
echo "📋 Git Status:"
git status --short

# Function to deploy
deploy() {
    echo "🔄 Starting deployment..."
    
    # Add all changes
    git add .
    
    # Get commit message from user
    read -p "📝 Enter commit message: " commit_msg
    
    # Commit changes
    git commit -m "$commit_msg"
    
    # Push to trigger workflow
    git push origin main
    
    echo "✅ Code pushed! Check GitHub Actions for deployment status:"
    echo "🔗 https://github.com/adriana-adri/quickaid/actions"
}

# Show options
echo ""
echo "Choose an option:"
echo "1) Deploy changes"
echo "2) Check deployment status"
echo "3) View workflow logs"

read -p "Enter choice (1-3): " choice

case $choice in
    1)
        deploy
        ;;
    2)
        echo "🔗 Opening GitHub Actions..."
        open "https://github.com/adriana-adri/quickaid/actions"
        ;;
    3)
        echo "📊 Recent workflow runs:"
        echo "Visit: https://github.com/adriana-adri/quickaid/actions"
        ;;
    *)
        echo "❌ Invalid choice"
        ;;
esac
