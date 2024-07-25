#!/bin/bash

CONFIG_DIR="$HOME/.config/floflis/flomem"
#SCRIPT_DIR="/usr/lib"
SCRIPT_NAME="flomem"

# Function to drop sudo privileges whenever it isn't needed anymore
drop_sudo() {
    # Drop sudo privileges
    if [ "$(id -u)" = "0" ]; then
       exec su -c "$0" "$SUDO_USER"
    fi
}

# Function to create the config directory and files
create_config() {
    mkdir -p "$CONFIG_DIR"
    cp config.sh "$CONFIG_DIR/config.sh"
    chmod +x "$CONFIG_DIR/config.sh"
}

# Function to create the action scripts
create_action_scripts() {
    cp action.89.sh "$CONFIG_DIR/action.89.sh"
    chmod +x "$CONFIG_DIR/action.89.sh"
    cp action.95.sh "$CONFIG_DIR/action.95.sh"
    chmod +x "$CONFIG_DIR/action.95.sh"
}

# Function to create the memory monitor script
create_monitor_script() {
    sudo cp -f "$SCRIPT_NAME" "/usr/lib/"
    sudo chmod +x "/usr/lib/$SCRIPT_NAME"
}

# Function to create a desktop entry for autostart
create_desktop_entry() {
    mkdir -p "$HOME/.config/autostart"
    cat > "$HOME/.config/autostart/flomem.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Floflis Memory Monitor
Exec=/usr/lib/$SCRIPT_NAME
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF
    chmod +x "$HOME/.config/autostart/flomem.desktop"
}

create_config
create_action_scripts
create_monitor_script
create_desktop_entry
drop_sudo

echo "It seems that Floflis Memory Monitor has been installed successfully!"