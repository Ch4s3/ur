#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
mkdir -p .march/Ur.app/Contents/MacOS
cat > .march/Ur.app/Contents/Info.plist <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleExecutable</key><string>Ur</string>
<key>CFBundleIdentifier</key><string>game.ur.prototype</string>
<key>CFBundleName</key><string>Ur</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>NSHighResolutionCapable</key><true/>
</dict></plist>
PLIST
cat > .march/Ur.app/Contents/MacOS/Ur <<'LAUNCH'
#!/bin/sh
set -eu
cd "$(dirname "$0")/../../../.."
export MARCH_PIN_MAIN=1
exec ./.march/build/release/ur
LAUNCH
chmod +x .march/Ur.app/Contents/MacOS/Ur
