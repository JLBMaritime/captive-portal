# Logo Directory

This directory is for storing the JLBMaritime logo that will be displayed on the captive portal.

## Requirements

1. Place the JLBMaritime logo file in this directory
2. Name the file **jlb_logo.png**
3. Recommended image dimensions: 200px × 200px
4. Format: PNG with transparency (preferred)

## Note

The installation script looks for a file named `jlb_logo.png` in this directory. If the file is not found, the installation will continue, but the logo will not be displayed on the captive portal page.

After installation, you can add or update the logo by copying it to:
```
/opt/captive-portal/static/logo/jlb_logo.png
```

Then restart the captive portal service:
```bash
sudo systemctl restart captive-portal.service
```
