# SanMar FTP to Box.com Integration

This script automates the process of downloading inventory data from SanMar's FTP server, converting it to CSV format, and uploading it to Box.com for import into Caspio.

## Files

- `sanmar_ftp_to_box.py`: Main script that handles downloading, converting, and uploading
- `requirements-box.txt`: Python dependencies
- `.env.box.sample`: Sample environment variables (rename to `.env` for local testing)

## Local Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements-box.txt
   ```
3. Copy `.env.box.sample` to `.env` and update if needed
4. Run the script:
   ```
   python sanmar_ftp_to_box.py
   ```

## Heroku Deployment

1. Create a new Heroku app:
   ```
   heroku create sanmar-inventory-import
   ```

2. Set environment variables:
   ```
   heroku config:set SANMAR_FTP_HOST=ftp.sanmar.com
   heroku config:set SANMAR_FTP_USER=6920
   heroku config:set SANMAR_FTP_PASSWORD=Sanmar20
   heroku config:set SANMAR_FTP_DIR=/SanMarPDD/
   heroku config:set SANMAR_FTP_FILENAME=sanmar_dip.txt
   heroku config:set BOX_CLIENT_ID=bapez65e9mnc3yg0yop17wy646pq57rs
   heroku config:set BOX_CLIENT_SECRET=wAZDgCAmVKOJH7PRbw1h74mDEs30uUZN
   heroku config:set BOX_FOLDER_ID=314832680593
   ```

3. Push to Heroku:
   ```
   git push heroku Box-FTP-Sanmar:main
   ```

4. Install the Heroku Scheduler add-on:
   ```
   heroku addons:create scheduler:standard
   ```

5. Open the scheduler dashboard:
   ```
   heroku addons:open scheduler
   ```

6. Add a new job with the following command to run daily:
   ```
   python sanmar_ftp_to_box.py
   ```

7. Set the frequency to "Daily" and choose an appropriate time (e.g., 2:00 AM UTC)

## Caspio Import

After the script runs, a CSV file will be available in your Box.com folder. You can then:

1. Log in to Caspio
2. Navigate to your Inventory table
3. Click "Import"
4. Select "Import from Box.com"
5. Select the CSV file
6. Map the fields and complete the import

## Troubleshooting

Check the logs for any errors:
```
heroku logs --tail
```

Common issues:
- FTP connection problems: Check FTP credentials and firewall settings
- Box.com authentication: Ensure Client ID and Secret are correct
- File format issues: Verify the SanMar file format hasn't changed