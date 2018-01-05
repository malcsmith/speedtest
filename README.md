# speedtest

This is a simple Docker container with 3 things
1. Speedtest-cli (downloaded - provides a www.speedtest.com speed check)
2. Simple python script to extract the results and write them to a database (hard coded at present)
3. Automate running via cron every 15 mins


TODO: Fix hardcoding for database credentials
TODO: Create database and table if not present
TODO: Randomise the time to run speedtest to flatten the load on speedtest servers.