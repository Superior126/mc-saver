<h1 align="center">MC Saver</h1>
<p align="center">MC Saver is a whole server backup solution that automatically backs up your Minecraft Server.</p>

> [!IMPORTANT]
> This package only works if you are using [docker](https://github.com/itzg/docker-minecraft-server) to host your Minecraft server. If you arn't, this solution is not for you. 

# Features
- Automated Backups
- Web Console

# How It Works
MC savef works by regularly creating a ZIP file of your server folder and saving it to Google Drive. MC Saver will automatically keep track of backups and allow you to restore to a specifc one when needed.

# Configurations
MC Saver can be condigured with diffrent options. Here are a list of the configurations and what they do.

- `backup-interval` - The amount of time in-bewteen each backup
- `keep-backups` - The number of backups that MC Saver should keep before deleting them. 
- `docker-container` - The name of the Docker container that hosts your server.
