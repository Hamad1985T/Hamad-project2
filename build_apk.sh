#!/bin/bash

# سكريبت لبناء ملف APK للتطبيق المحمول

echo "بدء عملية بناء ملف APK للتطبيق المحمول..."

# التأكد من وجود Flutter
if ! command -v flutter &> /dev/null; then
    echo "خطأ: Flutter غير مثبت. يرجى تثبيت Flutter أولاً."
    exit 1
fi

# الانتقال إلى مجلد التطبيق المحمول
cd "$(dirname "$0")/mobile"

# بناء نسخة APK
echo "جاري بناء نسخة APK..."
flutter build apk --release

# التحقق من نجاح عملية البناء
if [ $? -eq 0 ]; then
    echo "تم بناء نسخة APK بنجاح!"
    echo "مسار ملف APK: $(pwd)/build/app/outputs/flutter-apk/app-release.apk"
else
    echo "فشل في بناء نسخة APK. يرجى التحقق من الأخطاء أعلاه."
    exit 1
fi

echo "اكتملت عملية بناء نسخة APK بنجاح!"
