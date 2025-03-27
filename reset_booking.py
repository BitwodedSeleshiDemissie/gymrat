import json
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

BOOKINGS_FILE = 'bookings.json'

def reset_bookings():
    # Reset bookings to empty
    with open(BOOKINGS_FILE, 'w') as f:
        json.dump([], f)
    print("Bookings have been reset.")

def schedule_reset():
    # Schedule reset every Sunday at 6:00 AM
    scheduler = BackgroundScheduler()
    scheduler.add_job(reset_bookings, 'cron', day_of_week='sun', hour=6, minute=0)
    scheduler.start()
    print("Booking reset scheduled every Sunday at 6:00 AM.")
    
    # Keep the program running to allow the scheduler to run
    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

if __name__ == "__main__":
    # Call schedule_reset() to start the scheduled reset
    schedule_reset()
