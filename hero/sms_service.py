from sms_ir import SmsIr
from django.conf import settings


def send_sms(phone, message):
    """
    Send SMS using sms.ir API
    """
    try:
        sms_ir = SmsIr(
            api_key=settings.SMS_API_KEY,
            linenumber=settings.SMS_LINE_NUMBER,
        )
        
        result = sms_ir.send_sms(
            number=phone,
            message=message,
            linenumber=settings.SMS_LINE_NUMBER,
        )
        
        # Check status code
        if result.status_code == 200:
            return True, "SMS sent successfully"
        else:
            try:
                error_msg = result.json().get("message", "Unknown error")
            except:
                error_msg = "Unknown error"
            return False, f"Error {result.status_code}: {error_msg}"
            
    except Exception as e:
        return False, str(e)
