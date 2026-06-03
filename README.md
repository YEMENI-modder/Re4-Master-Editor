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
[![Github All Releases](https://img.shields.io/github/downloads/YEMENI-MODDER/Re4-Master-Editor/total.svg)](https://github.com/YEMENI-modder/Re4-Master-Editor/releases)


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
