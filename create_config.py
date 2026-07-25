import os

# Create .streamlit directory
os.makedirs(".streamlit", exist_ok=True)

# Create config.toml with proper content
config_content = """
[server]
enableXsrfProtection = false
enableCORS = false

[browser]
gatherUsageStats = false

[runner]
maxMessageSize = 100000000
"""

with open(".streamlit/config.toml", "w", encoding="utf-8") as f:
    f.write(config_content)

print("✅ config.toml created successfully!")