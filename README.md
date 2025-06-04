# 📘 ArchiMate Viewer

A lightweight Flask-based web app for visualizing `.archimate` files exported from [Archi](https://www.archimatetool.com/).  
Supports multiple diagrams per file, smart arrow drawing, and a dropdown to browse 100+ models.

---

## 📂 Features

- ✅ View `.archimate` files from the Archi modeling tool  
- ✅ Render multiple diagram views per file  
- ✅ Smart arrow routing (horizontal and vertical layout support)  
- ✅ Dropdown to select any file quickly (scalable to 100+ files)  
- ✅ Auto-sized canvas and clean name labels (no internal IDs)

---

## 🧰 Requirements

| Tool   | Version |
|--------|---------|
| Python | 3.7+    |
| Flask  | 2.0+    |

---

## 🖥️ Setup Instructions

### 1. 🔽 Clone or Download the Project

```bash
git clone https://github.com/yourname/archimate-viewer.git
cd archimate-viewer
```

### 2. 📁 Place Your `.archimate` Files

Create a folder named:

```
archimate_files/
```

Then place all your `.archimate` files inside:

```
archimate_files/
├── system_overview.archimate
├── business_model.archimate
└── cloud_architecture.archimate
```

Each file should contain:
- A valid XML model exported from Archi (`<archimate:model>`)
- At least one `<folder type="diagrams">` with `<element xsi:type="archimate:ArchimateDiagramModel">`

---

### 3. 📦 Install Dependencies

(Optional but recommended) Create a virtual environment:

```bash
python -m venv venv
```

Activate it:

- On **Windows**:
  ```bash
  venv\Scripts\activate
  ```

- On **macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```

Install Flask:

```bash
pip install flask
```

Or from the included `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

### 4. 🚀 Run the App

```bash
python app.py
```

Then open your browser and visit:

```
http://127.0.0.1:5000
```

---

## 📁 Folder Structure

```
archimate-viewer/
├── app.py
├── README.md
├── requirements.txt
├── archimate_files/
│   ├── model1.archimate
│   └── ...
```


## 🧠 Powered By

- Flask (Python Web Framework)
- SVG (for rendering diagrams)
- ArchiMate XML export
