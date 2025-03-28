# 🛡️ Django Auth & Data App

This project is a Django-based application that handles:

- **User Authentication & Session Management**  
- **Weather Data Retrieval from External APIs**  
- **Binance Coin Market Chart Visualization**

---

## 📦 Features

### 🔐 Authentication & Session Management
- CRUD operations for user sessions
- Profile updates with media support
- Custom authentication renderer

### 🌤 Weather App
- Integrates with external weather services
- Exposes clean REST APIs to fetch weather data

### 💰 Binance Coin Charting
- Fetches daily coin dump from Binance
- Plots daily market charts  
  _(Due to Binance API limitations, historical 30-day data is not supported)_

---

## 🚀 Getting Started

### 🛠️ Prerequisites
- Docker
- Docker Compose

### ⚙️ Setup & Run
```bash
docker-compose up --build

![data-flow](https://github.com/user-attachments/assets/ad5bf6c1-7297-4418-a233-028f71e5cb8d)


