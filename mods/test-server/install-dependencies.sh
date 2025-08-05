#!/bin/bash
# Install build dependencies for Luanti

echo "📦 Installing Luanti Build Dependencies"
echo "======================================"
echo

# Check if we can use sudo
if ! command -v sudo &> /dev/null; then
    echo "❌ sudo not found. Please install dependencies manually:"
    echo
    echo "apt-get update"
    echo "apt-get install build-essential cmake libjpeg-dev libpng-dev \\"
    echo "  libgl1-mesa-dev libsqlite3-dev libogg-dev libvorbis-dev \\"
    echo "  libopenal-dev libcurl4-gnutls-dev libfreetype6-dev zlib1g-dev \\"
    echo "  libgmp-dev libjsoncpp-dev libzstd-dev libsdl2-dev"
    exit 1
fi

echo "This script will install the following packages:"
echo "- Build tools: build-essential, cmake"
echo "- Graphics: libjpeg-dev, libpng-dev, libgl1-mesa-dev, libsdl2-dev"
echo "- Database: libsqlite3-dev"
echo "- Audio: libogg-dev, libvorbis-dev, libopenal-dev"
echo "- Network: libcurl4-gnutls-dev"
echo "- Other: libfreetype6-dev, zlib1g-dev, libgmp-dev, libjsoncpp-dev, libzstd-dev"
echo
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled"
    exit 1
fi

echo "🔄 Updating package list..."
sudo apt-get update

echo
echo "📥 Installing dependencies..."
sudo apt-get install -y \
    build-essential \
    cmake \
    libjpeg-dev \
    libpng-dev \
    libgl1-mesa-dev \
    libsqlite3-dev \
    libogg-dev \
    libvorbis-dev \
    libopenal-dev \
    libcurl4-gnutls-dev \
    libfreetype6-dev \
    zlib1g-dev \
    libgmp-dev \
    libjsoncpp-dev \
    libzstd-dev \
    libsdl2-dev \
    git

echo
echo "✅ Dependencies installed!"
echo
echo "You can now run ./build-vanilla.sh to build Luanti"