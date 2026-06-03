# RE4 Master Editor

[![Version](https://img.shields.io/badge/Version-1.0.0-red?style=flat-square)](https://github.com/YEMENI-modder/Re4-Master-Editor/releases/latest)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Winlator%20%7C%20Linux%20Wine-blue?style=flat-square)
[![Game](https://img.shields.io/badge/Game-RE4%20UHD%202014-darkred?style=flat-square)](https://store.steampowered.com/app/254700/Resident_Evil_4_2004/)
![Language](https://img.shields.io/badge/Language-AR%20%7C%20EN-green?style=flat-square)
![Codes](https://img.shields.io/badge/Codes-180%2B-orange?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-success?style=flat-square)
[![Built With Python](https://img.shields.io/badge/Built%20With-Python-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![Source Code](https://img.shields.io/badge/Source_Code-Claude_AI-purple?style=flat-square)](https://www.anthropic.com/claude)
![Visitors](https://visitor-badge.laobi.icu/badge?page_id=YEMENI-modder/RE4-Master-Editor)
[![Github All Releases](https://img.shields.io/github/downloads/YEMENI-modder/Re4-Master-Editor/total.svg)](https://github.com/YEMENI-modder/Re4-Master-Editor/releases)


## التعريف

Master Editor هي أداة Modding موحدة للعبة Resident Evil 4 Ultimate HD Edition، تجمع عدة أدوات ومحررات داخل برنامج واحد بواجهة بسيطة ومنظمة، بحيث يمكنك تعديل أغلب أنظمة اللعبة بدون الحاجة لاستخدام برامج HEX مثل HxD بشكل مباشر.

الأداة موجهة لمودرز RE4 وتوفر بيئة عمل أسهل وأسرع للتعديل على ملفات اللعبة والـ EXE.

---

# الأقسام

- Code Manager
- OSD Editor
- CNS Editor
- SND Editor *(قيد التطوير)*
- AEV Options Editor
- MDT Color Editor
- Room Init Editor
- Scripts
- Lock AEV with Key
- Weapons & Items Editor *(غير موجود في السورس كود)*

---

# شرح الأقسام

## Code Manager

قسم يحتوي على أكثر من 180 كود جاهز داخل واجهة واحدة.

يمكنك من خلاله:

- تفعيل أو إيقاف الأكواد.
- تعديل القيم بسهولة.
- تطبيق التعديلات مباشرة على `bio4.exe`.
- تشغيل الأكواد في الوضع العادي أو Real-Time.
- استخدام الأكواد بدون الحاجة إلى HxD.

الأكواد مرتبة داخل أقسام لتسهيل الوصول إليها.

---

## OSD Editor

هذا القسم مخصص لتعديل ملفات OSD.

وظيفة الملف مرتبطة بأنظمة مثل:

- حذف عناصر من الشنطة.
- تفعيل أحداث AEV.
- ربط الأحداث داخل اللعبة.

كل التعديلات تتم من خلال واجهة مرتبة ومناسبة لطبيعة الملف بدون الحاجة لتعديل HEX يدوي.

---

## CNS Editor

يمكنك من خلال هذا القسم تعديل الحدود القصوى الخاصة باللعبة مثل:

- عدد الأعداء.
- عدد التأثيرات.
- عدد المجسمات.
- Limits داخلية أخرى.

---

## SND Editor

القسم لا يزال قيد التطوير.

---

## AEV Options Editor

هذا القسم مخصص لتعديل رسائل AEV OPTION بسهولة.

يمكنك:

- فتح ملفات TXT.
- ربط الرسائل مع AEV.
- تعديل الأكواد الخاصة بالرسائل.
- مشاهدة شكل النص مباشرة كما سيظهر داخل اللعبة.

إذا كنت تعرف نظام AEV OPTION فسوف تفهم وظيفة القسم مباشرة.

---

## MDT Color Editor

يمكنك من خلاله:

- تعديل ألوان MDT.
- إنشاء ألوان مخصصة.
- معاينة شكل النص داخل اللعبة مباشرة.
- تعديل ألوان الرسائل بسهولة.

القسم مشابه لفكرة AEV OPTION من ناحية المعاينة المباشرة.

---

## Room Init Editor

هذا القسم يسمح لك بنقل برمجيات أي مرحلة إلى مرحلة أخرى بضغطة زر.

مثال:

- نقل برمجيات `R103` إلى `R107`.

---

## Scripts

قسم مخصص لتشغيل السكربتات والأدوات المساعدة المرتبطة بالتعديل على اللعبة.

---

## Lock AEV with Key

قسم مخصص للتحكم بملفات ربط الـ AEV بالمفاتيح.

يحتوي على:

- AVL Editor
- Event.cfg Editor

ويسمح بتعديل الملفات مباشرة من خلال واجهة رسومية بدون الحاجة لاستخدام HxD.

---

## Weapons & Items Editor

قسم ضخم لتعديل أنظمة الأسلحة والعناصر داخل اللعبة.

يمكنك تعديل:

- قوة الأسلحة.
- عدد التطويرات.
- أسعار التطويرات.
- عناصر التاجر.
- التطويرات المتوفرة عند التاجر.
- أسعار العناصر.
- مخزون العناصر.
- أنواع العناصر.
- حجم العناصر داخل الشنطة.
- دمج العناصر لإنتاج عناصر جديدة.
- العناصر التي تبدأ بها.
- مقدار الهيل والفلوس عند بداية اللعبة.
- والكثير من الخصائص الأخرى.

كل ذلك داخل واجهة بسيطة ومنظمة.

---

# مميزات الأداة

- واجهة سهلة وبسيطة.
- دعم اللغة العربية والإنجليزية.
- جميع الأدوات داخل برنامج واحد.
- تقليل الحاجة لاستخدام HxD في أغلب التعديلات.
- دعم التعديل المباشر على ملفات اللعبة.
- دعم التعديل الفوري (Real-Time).
- أكثر من 180 كود جاهز داخل Code Manager.
- نظام فحص التحديثات من GitHub.
- نظام Backup مدمج لبعض العمليات الحساسة.
- دعم ملفات متعددة خاصة بـ Resident Evil 4.
- معاينة مباشرة للنصوص والألوان داخل بعض الأقسام.
- دعم Winlator.
- دعم Linux عبر Wine.
- دعم Windows.
- لا تحتاج لتثبيت المكتبات يدوياً عند استخدام النسخة المجمعة.
- نظام أقسام موحد لتسهيل الوصول إلى الأدوات.

---

# لقطات من الأداة

<img width="1278" height="550" alt="Screenshot_20260514_171206" src="https://github.com/user-attachments/assets/7afccc66-4403-442e-aab1-de3ba3aa2bc2" />

<img width="1136" height="694" alt="Screenshot_20260514_171702" src="https://github.com/user-attachments/assets/3c2ce130-8bc6-43ed-9364-311699e9a817" />

<img width="1148" height="700" alt="Screenshot_20260514_172054" src="https://github.com/user-attachments/assets/750cf28e-6154-4b87-a7fd-eb643c39a4bd" />

<img width="1138" height="697" alt="Screenshot_20260514_172121" src="https://github.com/user-attachments/assets/f3644fe1-9d2e-4ef2-852a-0fa0dcadfb8c" />

<img width="1122" height="700" alt="Screenshot_20260514_172259" src="https://github.com/user-attachments/assets/be17c570-d1b6-487a-8a9a-6969f3e0c983" />

<img width="1136" height="696" alt="Screenshot_20260514_172335" src="https://github.com/user-attachments/assets/cb444b64-30b4-4be0-9785-7f73e8df371a" />

<img width="1135" height="697" alt="Screenshot_20260514_172353" src="https://github.com/user-attachments/assets/38066fee-eaf6-4864-ac3c-f6d901b435e8" />

<img width="1122" height="698" alt="Screenshot_20260514_172549" src="https://github.com/user-attachments/assets/d75de138-be16-48eb-a0da-b3364b5170de" />

<img width="1136" height="700" alt="Screenshot_20260514_172710" src="https://github.com/user-attachments/assets/ee80c472-b9f3-4490-b569-2a8c8ab06d7a" />

---
# الحقوق

## المشروع

- Project Owner: YEMENI
- Source Code: Claude AI
- Project Design & RE4 Research: YEMENI

## مساهمات خارجية

الأقسام التالية مستوحاة أو مبنية على أعمال PLAYER7Z:

- WAIE
- Room Init Editor

شكر خاص لـ PLAYER7Z على مساهماته وأعماله التي ساعدت في تطوير المشروع.

---

## الذكاء الاصطناعي

تمت كتابة السورس كود الخاص بالمشروع باستخدام Claude AI.

جميع تصميم الأقسام، تحديد الوظائف، تحليل ملفات Resident Evil 4، اختبار الميزات، اكتشاف الأخطاء، مراجعة النتائج، وتوجيه عملية التطوير تمت بواسطة YEMENI.
---

## الإبلاغ عن المشاكل

إذا واجهت أي مشكلة أو Bug أو لديك اقتراح لتحسين الأداة، يرجى فتح **Issue** في المستودع.
