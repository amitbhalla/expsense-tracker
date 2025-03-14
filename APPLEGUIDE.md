# Notes for Apple Silicon (M1/M2) Macs

## Python Installation

If you need to install Python on your Apple Silicon Mac:

1. Install Homebrew (the package manager for macOS):
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. Add Homebrew to your PATH:
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

3. Install Python:
```bash
brew install python
```

4. Verify the installation:
```bash
python3 --version
```

## Package Installation

All the required packages should work natively on Apple Silicon. If you encounter any issues:

1. Make sure you're using the latest pip:
```bash
pip install --upgrade pip
```

2. Install packages individually if one fails:
```bash
pip install django
pip install django-crispy-forms
pip install crispy-bootstrap5
pip install pandas
pip install matplotlib
```

## Troubleshooting Common Issues

### If the server won't start:
```bash
# Check for port conflicts
lsof -i :8000
# Use a different port if needed
python manage.py runserver 8080
```

### If migrations fail:
```bash
# Reset migrations (warning: this will delete your database)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
rm db.sqlite3
python manage.py makemigrations accounts transactions dashboard
python manage.py migrate
```

### If static files aren't loading:
```bash
# Collect static files
python manage.py collectstatic
```