from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import time
from datetime import datetime,timedelta
from app.dependencies import SessionDep,SessionLocal
from app.models.notes import Note
from app.models.posts import PostAttachment


scheduler = BackgroundScheduler()



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


def clean_orphan_post_attachments(db:SessionDep):
    deleted_count = db.query(PostAttachment).filter(PostAttachment.post_id == None).delete(synchronize_session=False)
    db.commit()
    print(f'{deleted_count} orphan post attachments have been deleted successfully')

def clean_orphan_post_attachments_job():
    db = SessionLocal()
    try:
        clean_orphan_post_attachments(db)
    finally:
        db.close()


scheduler.add_job(clean_notes_job,'interval',hours=1)
scheduler.add_job(clean_orphan_post_attachments_job,'interval',hours=24)