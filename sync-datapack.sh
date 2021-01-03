target_save=$1
rsync -avu --delete "turtleswarm-client" "$HOME/Library/ApplicationSupport/minecraft/saves/$target_save/datapacks"
