from sms_ir import SmsIr
from django.conf import settings


def send_sms(phone, message):
    """
    Send SMS using sms.ir API
    """
    try:
        print(f"[SMS Service] API Key: {settings.SMS_API_KEY[:10]}...")
        print(f"[SMS Service] Line Number: {settings.SMS_LINE_NUMBER}")
        
        sms_ir = SmsIr(
            api_key=settings.SMS_API_KEY,
            linenumber=settings.SMS_LINE_NUMBER,
        )
        
        result = sms_ir.send_sms(
            number=phone,
            message=message,
            linenumber=settings.SMS_LINE_NUMBER,
        )
        
        print(f"[SMS Service] Raw response: {result}")
        print(f"[SMS Service] Response type: {type(result)}")
        
        if hasattr(result, 'status_code'):
            if result.status_code == 200:
                return True, "SMS sent successfully"
            else:
                try:
                    error_msg = result.json().get("message", "Unknown error")
                except:
                    error_msg = "Unknown error"
                return False, f"Error {result.status_code}: {error_msg}"
        elif isinstance(result, dict):
            if result.get("status") == 1 or result.get("isSuccessful") == True:
                return True, "SMS sent successfully"
            else:
                error_msg = result.get("message", result.get("error", "Unknown error"))
                return False, f"Error: {error_msg}"
        else:
            return True, f"SMS sent (response: {result})"
            
    except Exception as e:
        print(f"[SMS Service] Exception: {e}")
        import traceback
        traceback.print_exc()
        return False, str(e)
