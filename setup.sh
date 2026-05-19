#!/bin/bash

echo "================================"
echo "LMS Project Setup Script"
echo "================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Step 1: Creating Virtual Environment...${NC}"
python -m venv venv

echo -e "${BLUE}Step 2: Activating Virtual Environment...${NC}"
source venv/bin/activate

echo -e "${BLUE}Step 3: Upgrading pip...${NC}"
pip install --upgrade pip

echo -e "${BLUE}Step 4: Installing Dependencies...${NC}"
pip install -r requirements.txt

echo -e "${BLUE}Step 5: Running Migrations...${NC}"
python manage.py makemigrations
python manage.py migrate

echo -e "${BLUE}Step 6: Creating Superuser...${NC}"
echo "Enter superuser credentials:"
python manage.py createsuperuser

echo -e "${BLUE}Step 7: Collecting Static Files...${NC}"
python manage.py collectstatic --noinput

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "To start the development server, run:"
echo "python manage.py runserver"
echo ""
echo "Access points:"
echo "  Admin: http://localhost:8000/admin/"
echo "  API Docs: http://localhost:8000/api/docs/"
