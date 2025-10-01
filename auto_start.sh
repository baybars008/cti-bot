#!/bin/bash

# CTI-BOT: Advanced Cyber Threat Intelligence Platform
# ===================================================
#
# Created by: Alihan Şahin | Baybars
# Threat & Security Researcher
#
# Website: https://alihansahin.com
# GitHub: https://github.com/baybars008
#
# Automated Startup Script
# ========================
# Comprehensive management system for all project tools and operations.
# Built with futuristic design principles and advanced automation capabilities.
#
# Mission: "To revolutionize cybersecurity through intelligent threat detection,
# predictive analytics, and automated response systems that stay ahead of
# evolving cyber threats."

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
END='\033[0m'

# Logo and header
show_logo() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    CTI-BOT v2.1.7                           ║"
    echo "║          Advanced Cyber Threat Intelligence Platform        ║"
    echo "║                Automated Startup Script                      ║"
    echo "║                    CLASSIFIED SYSTEM                         ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${END}"
}

# Help menu
show_help() {
    echo -e "${YELLOW}📋 CTI-BOT Automated Startup Menu:${END}"
    echo ""
    echo -e "${GREEN}🚀 Startup Options:${END}"
    echo "1. Start Flask application only"
    echo "2. Start data collection only"
    echo "3. Start full system (Flask + Data Collection)"
    echo "4. Start in background (nohup)"
    echo "5. Start with screen"
    echo "6. Start with Docker"
    echo ""
    echo -e "${BLUE}🔧 System Management:${END}"
    echo "7. Check system status"
    echo "8. Check database status"
    echo "9. Show log files"
    echo "10. Restart project"
    echo "11. Stop project"
    echo "12. System cleanup"
    echo ""
    echo -e "${PURPLE}🛠️  Installation & Maintenance:${END}"
    echo "13. Install required packages"
    echo "14. Setup/initialize database"
    echo "15. Performance optimization"
    echo "16. Cache system management"
    echo "17. Backup database"
    echo "18. System update"
    echo ""
    echo -e "${CYAN}📊 Analysis & Reporting:${END}"
    echo "19. Simple data analysis"
    echo "20. Sector analysis"
    echo "21. Real-time analysis"
    echo "22. Generate report"
    echo "23. Export data"
    echo ""
    echo -e "${YELLOW}🔗 Integrations:${END}"
    echo "24. Social media automation"
    echo "25. Email integration"
    echo "26. Slack integration"
    echo "27. Teams integration"
    echo ""
    echo -e "${RED}🧪 Testing & Validation:${END}"
    echo "28. API tests"
    echo "29. Database tests"
    echo "30. Redis connection test"
    echo "31. System performance test"
    echo ""
    echo -e "${WHITE}💡 Help:${END}"
    echo "32. Help menu"
    echo "33. System information"
    echo "0. Exit"
    echo ""
    echo -e "${YELLOW}💡 Usage: ./auto_start.sh [option]${END}"
    echo -e "${YELLOW}💡 Example: ./auto_start.sh 3${END}"
}

# Check project directory
check_project_dir() {
    PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [ ! -d "$PROJECT_DIR" ]; then
        echo -e "${RED}❌ Project directory not found: $PROJECT_DIR${END}"
        echo -e "${YELLOW}💡 Please ensure you're in the correct directory${END}"
        exit 1
    fi
    cd "$PROJECT_DIR"
    echo -e "${GREEN}✅ Changed to project directory: $(pwd)${END}"
}

# Check system status
check_system_status() {
    echo -e "${YELLOW}🔍 Checking System Status...${END}"
    echo ""
    
    # Python check
    if command -v python3 &> /dev/null; then
        echo -e "${GREEN}✅ Python3: $(python3 --version)${END}"
    else
        echo -e "${RED}❌ Python3 not found${END}"
    fi
    
    # Pip check
    if command -v pip3 &> /dev/null; then
        echo -e "${GREEN}✅ Pip3: $(pip3 --version)${END}"
    else
        echo -e "${RED}❌ Pip3 not found${END}"
    fi
    
    # Redis check
    if command -v redis-server &> /dev/null; then
        echo -e "${GREEN}✅ Redis: Installed${END}"
        if redis-cli ping > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Redis: Running${END}"
        else
            echo -e "${YELLOW}⚠️  Redis: Installed but not running${END}"
        fi
    else
        echo -e "${RED}❌ Redis not found${END}"
    fi
    
    # Virtual environment check
    if [ -d "venv" ]; then
        echo -e "${GREEN}✅ Virtual Environment: Available${END}"
    else
        echo -e "${YELLOW}⚠️  Virtual Environment: Not found${END}"
    fi
    
    # Database check
    if [ -f "instance/data.db" ]; then
        echo -e "${GREEN}✅ Database: Available${END}"
        # Check data count
        if command -v sqlite3 &> /dev/null; then
            POST_COUNT=$(sqlite3 instance/data.db "SELECT COUNT(*) FROM posts;" 2>/dev/null || echo "0")
            echo -e "${BLUE}📊 Posts: $POST_COUNT records${END}"
        fi
    else
        echo -e "${YELLOW}⚠️  Database: Not found${END}"
    fi
    
    # Port check
    if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Port 5000: In use (Flask running)${END}"
    else
        echo -e "${YELLOW}⚠️  Port 5000: Available${END}"
    fi
}

# Start Flask application
start_flask_app() {
    echo -e "${YELLOW}🚀 Starting Flask Application...${END}"
    
    # Activate virtual environment
    if [ -d "venv" ]; then
        source venv/bin/activate
        echo -e "${GREEN}✅ Virtual environment activated${END}"
    else
        echo -e "${RED}❌ Virtual environment not found!${END}"
        echo -e "${YELLOW}💡 Please run option '13' first${END}"
        exit 1
    fi
    
    # Check required packages
    if [ -f "requirements.txt" ]; then
        echo -e "${YELLOW}📦 Checking packages...${END}"
        pip install -r requirements.txt > /dev/null 2>&1
        echo -e "${GREEN}✅ Packages ready${END}"
    fi
    
    # Start Redis
    echo -e "${YELLOW}🔄 Starting Redis...${END}"
    sudo systemctl start redis-server 2>/dev/null || echo -e "${YELLOW}⚠️  Redis already running${END}"
    
    # Check database
    if [ ! -f "instance/data.db" ]; then
        echo -e "${YELLOW}📦 Creating database...${END}"
        python3 setup_database.py
        echo -e "${GREEN}✅ Database created${END}"
    else
        echo -e "${GREEN}✅ Database available${END}"
    fi
    
    # Environment variables
    export FLASK_APP=app.py
    export FLASK_ENV=development
    export FLASK_DEBUG=1
    export PYTHONPATH="${PWD}:${PYTHONPATH}"
    
    echo -e "${GREEN}✅ CTI-BOT started!${END}"
    echo -e "${CYAN}🌐 Dashboard: http://localhost:5000/dashboard${END}"
    echo -e "${CYAN}📊 API Health: http://localhost:5000/api/health${END}"
    echo ""
    echo -e "${YELLOW}⏹️  Press Ctrl+C to stop${END}"
    
    # Start Flask application
    python3 app.py
}

# Start data collection
start_data_collection() {
    echo -e "${YELLOW}📊 Starting Data Collection Process...${END}"
    
    # Activate virtual environment
    if [ -d "venv" ]; then
        source venv/bin/activate
        echo -e "${GREEN}✅ Virtual environment activated${END}"
    else
        echo -e "${RED}❌ Virtual environment not found!${END}"
        exit 1
    fi
    
    # Setup database
    echo -e "${YELLOW}1️⃣ Setting up database...${END}"
    python3 setup_database.py
    
    # Add sample data
    echo -e "${YELLOW}2️⃣ Adding sample data...${END}"
    python3 -c "
import sys
sys.path.append('.')
from background_jobs.cron_update_db import add_sample_data
add_sample_data()
print('✅ Sample data added')
"
    
    # Start real data collection
    echo -e "${YELLOW}3️⃣ Starting real data collection...${END}"
    python3 background_jobs/cron_update_db.py
    
    echo -e "${GREEN}✅ Data collection completed!${END}"
}

# Start full system
start_full_system() {
    echo -e "${BLUE}🚀 Starting Full System...${END}"
    
    # Activate virtual environment
    if [ -d "venv" ]; then
        source venv/bin/activate
        echo -e "${GREEN}✅ Virtual environment activated${END}"
    else
        echo -e "${RED}❌ Virtual environment not found!${END}"
        echo -e "${YELLOW}💡 Please run option '13' first${END}"
        exit 1
    fi
    
    # Start project in background
    echo -e "${YELLOW}1️⃣ Starting project...${END}"
    nohup python3 app.py > flask.log 2>&1 &
    FLASK_PID=$!
    
    # Wait 5 seconds
    sleep 5
    
    # Setup database
    echo -e "${YELLOW}2️⃣ Setting up database...${END}"
    if ! python3 setup_database.py; then
        echo -e "${RED}❌ Database setup error!${END}"
        kill $FLASK_PID 2>/dev/null
        exit 1
    fi
    
    # Add sample data
    echo -e "${YELLOW}3️⃣ Adding sample data...${END}"
    python3 -c "
import sys
sys.path.append('.')
from background_jobs.cron_update_db import add_sample_data
add_sample_data()
print('✅ Sample data added')
"
    
    # Start real data collection in background
    echo -e "${YELLOW}4️⃣ Starting real data collection...${END}"
    nohup python3 background_jobs/cron_update_db.py > data.log 2>&1 &
    DATA_PID=$!
    
    echo -e "${GREEN}✅ Full system started!${END}"
    echo -e "${CYAN}🌐 Dashboard: http://localhost:5000/dashboard${END}"
    echo -e "${CYAN}📊 Flask Log: tail -f flask.log${END}"
    echo -e "${CYAN}📊 Data Log: tail -f data.log${END}"
    echo -e "${YELLOW}⏹️  To stop: kill $FLASK_PID $DATA_PID${END}"
}

# Install packages
install_packages() {
    echo -e "${YELLOW}📦 Installing Required Packages...${END}"
    
    # Check Python3 and pip3 installation
    if ! command -v python3 &> /dev/null; then
        echo -e "${YELLOW}📦 Installing Python3...${END}"
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv
    fi
    
    if ! command -v pip3 &> /dev/null; then
        echo -e "${YELLOW}📦 Installing pip3...${END}"
        sudo apt install -y python3-pip
    fi
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}🔧 Creating virtual environment...${END}"
        python3 -m venv venv
        echo -e "${GREEN}✅ Virtual environment created${END}"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    echo -e "${GREEN}✅ Virtual environment activated${END}"
    
    # Update pip
    pip install --upgrade pip
    
    # Install required packages
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        echo -e "${GREEN}✅ Packages installed${END}"
    fi
    
    # Check Redis installation
    if ! command -v redis-server &> /dev/null; then
        echo -e "${YELLOW}📦 Installing Redis...${END}"
        sudo apt update
        sudo apt install -y redis-server
        echo -e "${GREEN}✅ Redis installed${END}"
    fi
    
    echo -e "${GREEN}✅ Installation completed!${END}"
}

# Setup database
setup_database() {
    echo -e "${YELLOW}📦 Setting up Database...${END}"
    
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    python3 setup_database.py
    echo -e "${GREEN}✅ Database setup completed!${END}"
}

# Stop system
stop_system() {
    echo -e "${YELLOW}🛑 Stopping CTI-BOT...${END}"
    
    # Stop processes on port 5000
    echo -e "${BLUE}🔍 Checking processes on port 5000...${END}"
    PORT_PIDS=$(sudo lsof -ti:5000 2>/dev/null)
    
    if [ ! -z "$PORT_PIDS" ]; then
        echo -e "${BLUE}📊 Found processes: $PORT_PIDS${END}"
        echo -e "${YELLOW}🛑 Stopping processes...${END}"
        echo $PORT_PIDS | xargs sudo kill -9
        echo -e "${GREEN}✅ Port 5000 cleared${END}"
    else
        echo -e "${YELLOW}ℹ️  No processes found on port 5000${END}"
    fi
    
    # Stop Flask processes
    echo -e "${BLUE}🔍 Checking Flask processes...${END}"
    FLASK_PIDS=$(ps aux | grep -E "(flask|app\.py)" | grep -v grep | awk '{print $2}')
    
    if [ ! -z "$FLASK_PIDS" ]; then
        echo -e "${BLUE}📊 Found Flask processes: $FLASK_PIDS${END}"
        echo -e "${YELLOW}🛑 Stopping Flask processes...${END}"
        echo $FLASK_PIDS | xargs kill -9
        echo -e "${GREEN}✅ Flask processes stopped${END}"
    else
        echo -e "${YELLOW}ℹ️  No Flask processes found${END}"
    fi
    
    # Stop data collection processes
    echo -e "${BLUE}🔍 Checking data collection processes...${END}"
    CRON_PIDS=$(ps aux | grep cron_update_db.py | grep -v grep | awk '{print $2}')
    
    if [ ! -z "$CRON_PIDS" ]; then
        echo -e "${BLUE}📊 Found data collection processes: $CRON_PIDS${END}"
        echo -e "${YELLOW}🛑 Stopping data collection processes...${END}"
        echo $CRON_PIDS | xargs kill -9
        echo -e "${GREEN}✅ Data collection processes stopped${END}"
    else
        echo -e "${YELLOW}ℹ️  No data collection processes found${END}"
    fi
    
    echo -e "${GREEN}🎉 CTI-BOT successfully stopped!${END}"
}

# Show logs
show_logs() {
    echo -e "${YELLOW}📋 Log Files:${END}"
    
    if [ -f "flask.log" ]; then
        echo -e "${BLUE}📊 Flask Log (last 20 lines):${END}"
        tail -20 flask.log
    else
        echo -e "${YELLOW}ℹ️  flask.log not found${END}"
    fi
    
    if [ -f "data.log" ]; then
        echo -e "${BLUE}📊 Data Log (last 20 lines):${END}"
        tail -20 data.log
    else
        echo -e "${YELLOW}ℹ️  data.log not found${END}"
    fi
}

# Clean system
clean_system() {
    echo -e "${YELLOW}🧹 Cleaning System...${END}"
    
    # Clean log files
    if [ -f "flask.log" ]; then
        rm flask.log
        echo -e "${GREEN}✅ flask.log cleaned${END}"
    fi
    
    if [ -f "data.log" ]; then
        rm data.log
        echo -e "${GREEN}✅ data.log cleaned${END}"
    fi
    
    # Clean cache
    if [ -d "__pycache__" ]; then
        rm -rf __pycache__
        echo -e "${GREEN}✅ __pycache__ cleaned${END}"
    fi
    
    # Clean Redis cache
    if command -v redis-cli &> /dev/null; then
        if redis-cli ping > /dev/null 2>&1; then
            redis-cli FLUSHALL
            echo -e "${GREEN}✅ Redis cache cleaned${END}"
        fi
    fi
    
    echo -e "${GREEN}✅ System cleaned!${END}"
}

# Main menu
main_menu() {
    show_logo
    check_project_dir
    
    if [ $# -eq 0 ]; then
        show_help
        echo ""
        read -p "Select your option (1-33): " choice
    else
        choice=$1
    fi
    
    case $choice in
        1)
            start_flask_app
            ;;
        2)
            start_data_collection
            ;;
        3)
            start_full_system
            ;;
        4)
            echo -e "${BLUE}🚀 Starting in background...${END}"
            start_full_system
            ;;
        5)
            echo -e "${BLUE}🚀 Starting with screen...${END}"
            screen -dmS cti_bot python3 app.py
            screen -dmS cti_data python3 background_jobs/cron_update_db.py
            echo -e "${GREEN}✅ Started with screen!${END}"
            echo -e "${YELLOW}📺 Connect to Flask screen: screen -r cti_bot${END}"
            echo -e "${YELLOW}📺 Connect to Data screen: screen -r cti_data${END}"
            ;;
        6)
            echo -e "${BLUE}🚀 Starting with Docker...${END}"
            docker-compose up -d
            ;;
        7)
            check_system_status
            ;;
        8)
            if [ -f "instance/data.db" ]; then
                sqlite3 instance/data.db ".tables"
                sqlite3 instance/data.db "SELECT COUNT(*) as total_posts FROM posts;"
            else
                echo -e "${RED}❌ Database not found${END}"
            fi
            ;;
        9)
            show_logs
            ;;
        10)
            stop_system
            sleep 2
            start_full_system
            ;;
        11)
            stop_system
            ;;
        12)
            clean_system
            ;;
        13)
            install_packages
            ;;
        14)
            setup_database
            ;;
        15)
            echo -e "${YELLOW}Performance optimization feature coming soon${END}"
            ;;
        16)
            echo -e "${YELLOW}Cache system management feature coming soon${END}"
            ;;
        17)
            if [ -f "instance/data.db" ]; then
                timestamp=$(date +"%Y%m%d_%H%M%S")
                backup_file="backup_data_${timestamp}.db"
                cp instance/data.db "$backup_file"
                echo -e "${GREEN}✅ Database backed up: $backup_file${END}"
            else
                echo -e "${RED}❌ Database not found${END}"
            fi
            ;;
        18)
            echo -e "${YELLOW}System update feature coming soon${END}"
            ;;
        19)
            echo -e "${YELLOW}Simple data analysis feature coming soon${END}"
            ;;
        20)
            echo -e "${YELLOW}Sector analysis feature coming soon${END}"
            ;;
        21)
            echo -e "${YELLOW}Real-time analysis feature coming soon${END}"
            ;;
        22)
            echo -e "${YELLOW}Report generation feature coming soon${END}"
            ;;
        23)
            echo -e "${YELLOW}Data export feature coming soon${END}"
            ;;
        24)
            echo -e "${YELLOW}Social media automation feature coming soon${END}"
            ;;
        25)
            echo -e "${YELLOW}Email integration feature coming soon${END}"
            ;;
        26)
            echo -e "${YELLOW}Slack integration feature coming soon${END}"
            ;;
        27)
            echo -e "${YELLOW}Teams integration feature coming soon${END}"
            ;;
        28)
            echo -e "${YELLOW}API tests feature coming soon${END}"
            ;;
        29)
            echo -e "${YELLOW}Database tests feature coming soon${END}"
            ;;
        30)
            echo -e "${YELLOW}Redis connection test feature coming soon${END}"
            ;;
        31)
            echo -e "${YELLOW}System performance test feature coming soon${END}"
            ;;
        32)
            show_help
            ;;
        33)
            echo -e "${CYAN}💻 System Information${END}"
            echo -e "${BLUE}Project Directory:${END} $(pwd)"
            echo -e "${BLUE}Python Version:${END} $(python3 --version 2>/dev/null || echo 'Not found')"
            echo -e "${BLUE}Operating System:${END} $(uname -s)"
            ;;
        0)
            echo -e "${CYAN}👋 Exiting CTI-BOT Automated Startup System...${END}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Invalid option!${END}"
            echo -e "${YELLOW}💡 For help: ./auto_start.sh${END}"
            exit 1
            ;;
    esac
}

# Run script
main_menu "$@"
