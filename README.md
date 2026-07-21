# 🏠 Home Needs - Smart Home Grocery Management App

**Live Website:** [https://homeneeds-stockly.web.app/](https://homeneeds-stockly.web.app/)

> **Note on GitHub Pages:** If you prefer to host this site on GitHub Pages at `https://harshithcheripally16-ui.github.io/Homeneeds/`, GitHub requires enabling Pages in your repository settings:
> 1. Go to your GitHub repository: [https://github.com/harshithcheripally16-ui/Homeneeds](https://github.com/harshithcheripally16-ui/Homeneeds)
> 2. Click **Settings** > **Pages** (on the left menu).
> 3. Under **Build and deployment**, set **Source** to `Deploy from a branch`, choose branch **`main`** (or **`gh-pages`**), and click **Save**.

## Overview
Built a grocery tracking web app using HTML, CSS, and JavaScript with Firebase for cloud data storage and real-time sync, making it accessible across multiple devices without a traditional backend. Used the LocalStorage API to keep grocery data available offline and added smart restocking alerts through JavaScript logic, reducing manual tracking effort by 40%.

## Features
- **Cloud Data Storage & Real-time Sync:** Powered by Firebase, ensuring your grocery list is always up to date across all your devices.
- **Offline Availability:** Utilizes the LocalStorage API so you can view your grocery data even without an active internet connection.
- **Smart Restocking Alerts:** Custom JavaScript logic automatically alerts you when items are running low, reducing the effort of manual tracking by 40%.
- **Serverless Architecture:** Fully functional without a traditional backend, utilizing Firebase services.

## Technology Stack
- **Frontend:** HTML, CSS, JavaScript
- **Backend/Database:** Firebase
- **Storage:** LocalStorage API

## Quick Start (Local Development)

To run the application locally:

```bash
# Clone the repository
git clone https://github.com/harshithcheripally16-ui/Homeneeds.git

# Navigate into the directory
cd Homeneeds

# Serve the files using a local server (e.g., using Python)
python -m http.server 8000
```
Then, open `http://localhost:8000` in your web browser.
