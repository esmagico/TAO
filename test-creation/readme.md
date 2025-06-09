# 🧪 TAO QTI Test Creation

### 1. ✅ Prerequisites

* Python **3.10+** installed
* Unix-like system (Linux/macOS)
* TAO instance running and accessible

### 2. 🛠 Setup & Run

Just run the provided script:

```bash
bash test.creation.sh
```

This will:

* Create and activate a Python virtual environment
* Install all required dependencies
* (Optional) Convert your Excel file to QTI `.zip` packages
* Upload the QTI `.zip` named qti_output files to your TAO instance

### 3. 📁 Required Files

* `test.creation.sh`: The setup and execution script
* `.env`: TAO credentials and base URL, placed in the same directory

```dotenv
# .env
TAO_BASE_URL=http://localhost:8080
TAO_USERNAME=admin
TAO_PASSWORD=admin
```

* (Optional) `data/quizzes.xlsx`: Your Excel file with quiz data