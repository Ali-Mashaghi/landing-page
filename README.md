# وب‌سایت شخصی علی مشاغی

وب‌سایت شخصی و نمونه کارهای علی مشاغی، توسعه‌دهنده فول‌استک و طراح رابط کاربری.

## تکنولوژی‌ها

- **Backend:** Django 6.0
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite
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
