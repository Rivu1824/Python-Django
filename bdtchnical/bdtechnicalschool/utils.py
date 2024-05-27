import uuid
from django.utils import timezone

def generate_unique_transaction_id():
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S%f') 
    unique_id = str(uuid.uuid4().hex)[:8]  
    return f"{timestamp}-{unique_id}"
