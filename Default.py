# In list_channels():
for ch in channels:
    real_url = client.get_stream_url(ch["id"])
    if not real_url:
        continue  # skip channels without working streams
    ch["stream_url"] = real_url
    # ... rest of the loop
  
