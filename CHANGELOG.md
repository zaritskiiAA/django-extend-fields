### Change log

## [0.1.0] - 09.10.2024

- Добавлен TranslatedField
- Добавлен ExtendMeta для моделей djnago.
- Добавлен единый интерфейс с django ORM для создания/обновления объектов через дескриптор TranslatedField.

## [0.2.0] - 10.10.2024

- Добавлена возможность авто транслирования для TranslatedField
- Добавлен DeeplTranslator как транслятор из коробки

## [0.3.0] - 11.10.2024

- Добавлен определитель языка AWSLanguageDetector.
- Добавлена возможность указывать авто транслятор как в параметре auto, так и в ExtendMeta.

## [0.4.0] - 11.10.2024

- Добавлен в AWSLanguageDetector новый прокси api метод batch_detect_languages