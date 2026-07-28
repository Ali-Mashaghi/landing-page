#(میتونه برای هر کسی باشه ) وب‌سایت شخصی علی مشاغی

وب‌سایت شخصی و نمونه کارهای علی مشاغی، توسعه‌دهنده فول‌استک و طراح رابط کاربری.

## تکنولوژی‌ها

- **Backend:** Django 6.0
- **Frontend:** HTML, CSS, JavaScript
- **Database:** PostgreSQL
- **API:** Django REST Framework
- **Deployment:** Gunicorn

## ویژگی‌ها

- صفحه اصلی با معرفی و خدمات
- صفحه پروژه‌ها
- صفحه رزومه
- فرم تماس با قابلیت ارسال پیامک
- طراحی ریسپانسیو
- پشتیبانی از تقویم فارسی (Jalali)

## نصب و اجرا

```bash
# نصب وابستگی‌ها
pip install -r requirements.txt

# اجرای مایگریشن‌ها
python manage.py migrate

# اجرای سرور
python manage.py runserver
```

## ذخیره فایل‌های آپلودی در Liara

فایل‌سیستم کانتینر Liara فقط‌خواندنی و موقتی است. برای تصویر پروفایل، رزومه و
تصاویر پروژه یک Object Storage سازگار با S3 بسازید و متغیرهای زیر را در تنظیمات
برنامه Liara وارد کنید:

```env
S3_BUCKET_NAME=your-bucket-name
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_ENDPOINT_URL=https://your-s3-endpoint
S3_REGION_NAME=us-east-1
S3_QUERYSTRING_AUTH=False
```

برای نمایش عمومی تصاویر، دسترسی خواندن Bucket را عمومی کنید. در صورت خصوصی بودن
Bucket، مقدار `S3_QUERYSTRING_AUTH` را روی `True` قرار دهید.

## ساختار پروژه

```
landing-page/
├── config/          # تنظیمات پروژه Django
├── hero/            # اپلیکیشن اصلی
├── Templates/       # قالب‌های HTML
├── static/          # فایل‌های استاتیک (CSS, JS, تصاویر)
├── media/           # فایل‌های آپلود شده
└── manage.py        # فایل مدیریت Django
```

## مجوز

تمامی حقوق محفوظ است.
