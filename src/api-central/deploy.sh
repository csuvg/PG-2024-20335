#!/bin/bash

echo "Deploying API Central..."

# Pull changes from GitHub
echo "Pulling changes from GitHub..."

# Activate the virtual environment
echo "Activating virtual environment..."
source /srv/web-apps/api-central/venv/bin/activate

# Make migrations and upgrade database
echo "Making migrations and updating database..."
flask db migrate -m "Agregar tabla Dictionary y actualizar modelos"

echo "Upgrading database..."
flask db upgrade

# Restart Gunicorn and Nginx services
echo "Restarting Gunicorn and Nginx..."
sudo systemctl restart api-central.service
sudo systemctl restart nginx

# Check if seed needs to be run
if [ "$1" -eq 1 ]; then
    echo "Running seed script..."
    python seed.py
else
    echo "Skipping seed script."
fi

echo "Deployment complete!"
