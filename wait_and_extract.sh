#!/bin/bash
TARGET_SIZE=606144431 # 578MB

echo "Monitoring MDVR-KCL download progress..."
while true; do
    if [ -f raw_data/mdvr_kcl/MDVR_KCL.zip ]; then
        SIZE=$(stat -f%z raw_data/mdvr_kcl/MDVR_KCL.zip 2>/dev/null || stat -c%s raw_data/mdvr_kcl/MDVR_KCL.zip 2>/dev/null)
        MB=$((SIZE / 1024 / 1024))
        PERCENT=$((SIZE * 100 / TARGET_SIZE))
        echo "Downloaded: ${MB}MB / 578MB (${PERCENT}%)"
        if [ "$SIZE" -ge "$TARGET_SIZE" ]; then
            echo "Download complete! Unzipping dataset..."
            unzip -q -o raw_data/mdvr_kcl/MDVR_KCL.zip -d raw_data/mdvr_kcl/
            echo "Unzip complete! Listing contents:"
            ls -la raw_data/mdvr_kcl/
            break
        fi
    fi
    sleep 5
done
