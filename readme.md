# Lucky AI for Telegram project

## Prerequisites
1. install python
2. install git
3. setup your github ssh keys properly

## Installation
### Cloning, get the code
```bash
git clone git@github.com:neotherack/lucky_ai_telegram.git
```

### Setup env for Linux
```bash
cd lucky_ai_telegram
python3 -m venv venv
venv\bin\python -m pip install --upgrade pip
venv\bin\pip install --upgrade -r requests.txt
```

### Setup env for Windows
```bash
cd lucky_ai_telegram
python -m venv venv
venv\Scripts\python -m pip install --upgrade pip
venv\Scripts\pip install --upgrade -r requests.txt
```

## Run program
### Linux
```bash
venv\bin\python3  aibot.py
```
### Windows
```bash
venv\Scripts\python aibot.py
```