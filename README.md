# McStatus
 
Simple bot for displaying whether or not a Minecraft server is online at a given time. Can also display the number of 
players currently connected to the server. 

# Command Usage: 

Prefix: %

# Help

   **Syntax:**
%help

   **Usage:**
Show a list of all commands the bot has to offer.

# ServerStatus

   **Syntax:**
%serverStatus &lt;address&gt; [port=25565]

   **Usage:**
Displays the online status of a server and how many players are currently connected.
# Status

   **Syntax:**
%status

   **Usage:**
Displays the online status of the default server and how many players are currently connected.

# PlayersOnline

   **Syntax:**
%playersOnline

   **Usage:**
Lists the players online on the default server.

# SetDefaultServer

   **Syntax:**
%setDefaultServer &lt;address&gt; [port=25565]

   **Usage:**
Sets the server whose status will be tracked for the discord server the command is run in.

# RemoveDefaultServer

   **Syntax:**
%removeDefaultServer

   **Usage:**
Sets the default server to none.

# ToggleNick

   **Syntax:**
%toggleNick

   **Usage:**
Toggles whether the nick of the bot will become online and offline

# ListBotPerms

   **Syntax:**
%listBotPerms

   **Usage:**
List what roles have the bot's admin commands

# AddBotPerms 

   **Syntax:**
%addBotPerms &lt;role&gt;

   **Usage:**
Allows a role to use all admin commands of the bot except %addBotPerms and %removeBotPerms.

# RemoveBotPerms

   **Syntax:**
%removeBotPerms

   **Usage:**
Removes a role's ability to use admin commands of the bot.
