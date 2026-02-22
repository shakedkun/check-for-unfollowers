# Instagram Unfollower Detector

A simple FastAPI tool to compare your Instagram Followers vs. Following list to see who isn't following you back.

## How to use

### 1. Export Data from Instagram
You need to request your data from Instagram. 
1. Go to **Settings** > **Your Activity** > **Download your information**.
2. Select **"Followers and following"**.
3. **Important:** Select **JSON** as the format (not HTML).

![Instagram Export Settings](assets/export_settings.png)

### 2. Setup
```bash
pip install -r requirements.txt
