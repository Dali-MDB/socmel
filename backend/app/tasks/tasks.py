from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import time
from datetime import datetime,timedelta
from app.dependencies import SessionDep,SessionLocal
from app.models.notes import Note


scheduler = BackgroundScheduler()

# def scheduled_task():
#     print(f"⏰ Task executed at {time.strftime('%X')}")


# def task2():
#     print(f"putain zebi")

# def task3():
#     print(f"putunfrtggg zebi")


# from datetime import datetime,timedelta
# scheduler.add_job(scheduled_task,"interval",minutes=1)
# scheduler.add_job(task2,'cron',hour=22,minute=56)
# run_time = datetime.now() + timedelta(seconds=30)
# scheduler.add_job(task3, "date", run_date=run_time)



def clean_notes(db:SessionDep):
    cutoff = datetime.now() - timedelta(hours=24)
    deleted_count = db.query(Note).filter(Note.created_at < cutoff).delete(synchronize_session=False)
    db.commit()
    print(f'{deleted_count} notes have been deleted successfully')

def clean_notes_job():
    db = SessionLocal()
    try:
        clean_notes(db)
    finally:
        db.close()


scheduler.add_job(clean_notes_job,'interval',hours=1)