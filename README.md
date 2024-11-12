### django-extend-fields

Расширенные возможности *django fields*. :guitar:

#### *Содержание*
1. [Проблемы, которые решает.](#problems)
2. [Установка пакета.](#package)
3. [Базовае использование.](#basic-usage)
4. [ExtendField и дополнительные возможности](#extend-field-opportunity)
5. [Dev запуск и тестирование.](#dev)

<br>

### 1. Проблемы, которые решает <a id="problems"></a>

- Авто-генерация полей таблиц бд.
- Сохранение единого интерфейса нового функционала с django.
- Готовые *API* по авто-транслитированию/детектированию языков.
- Автоматизизация рутинных процессов связанных с django fields.

### 2. ~~Установка пакета~~ <a id="package"></a>
в процессе

### 3. Базовае использование <a id="basic-usage"></a>


```
# settings.py

LANGUAGES = [
    ("en-us", "English"),
    ("ru", "Russian"),
    ("de", "Deautsch"),
]

# models.py

from django.utils.translation import gettext_lazy as _
from extends import TranslatedField


class Question(models.Model):

    question = TranslatedField(
        models.CharField(_("question"), max_length=200),
    )
```

TranslatedField, сгенерирует поля таблице question  в соответствии с языками закрепленными в константе `LANGUAGES`


| id          |question_en_us | question_ru   | question_de |
| :---        |    :----:     |        :----: |      ---:   |

В сигнатуру TranslatedField в качестве исходного поля можно передавать любой *django field*, которые принимает тип данных __str__.

Объект можно создать с помощью ООП `python` и  функционала `django`, например:

```
q = Question(question="hi")
q.save()
```
или 
```
q = Question.objects.create(question="hi")
```
или
```
q = Question.objects.create(question_en_us="hi") или Question(question_en_us="hi")
```

Что касается сохранения возможностей `django orm` совместно с `extend-field`, то реализована возможность только для методов `.create` и `.update` (beta).

Более подробно про возможности TranslatedField в разделе 4. [ExtendField и дополнительные возможности](#extend-field-opportunity)

### 4. ExtendField и дополнительные возможности <a id="extend-field-opportunity"></a> 

#### TanslatedField

[Вдохновлялся](https://pypi.org/project/django-translated-fields/), незначительная часть функционала осталась работоспособной. Например контекстный менеджер `django.utils.translation.override`


```
class TranslatedField(ExtendFieldDescriptor, ConverterMixin):

    def __init__(
        self,
        field: Field,
        specific=None,
        *,
        attr_suffix=None,
        attrgetter=translated_attrgetter,
        attrsetter=translated_attrsetter,
        auto=None,
        validators=None,
    ) -> None:
```

Сам по себе `TranslatedField` представляет дескриптор и имеет `django` -вский метод `contribute_to_class`, который во время инициализации вызывается для каждого *django field*.

`translated_attrgetter` и `translated_attrsetter` - расширяют дендер-методы дескриптора `__get__`, `__set__` для гибкости их изменения в зависимости от необходимости.

`auto` - атрибут добавляет возможность для авто-транслитирования текста. Представляет из себя кортеж из 2х элементов `converter` и `suffixes`.

`converter` - объект, чей интерфейс используется для транслитирования текста. В пакете есть готовые решения, например extends.opportunity.DeeplTranslator(детально про `DeeplTranslator` ниже.), который можно передать в качестве аргумента использовав функцию:
```
from extends.opportunity import get_translator
```
Вы, также, можете использовать свои решение, главное соблюдать обратную совместимость с `extends.opportunity.bace.TranslatorBase` и `extends.opportunity.TextResultModel`

`suffixes` - поля подлежащие авто-транслитированию, если не передан, транслитируются все поля.

`validators` - (список call объекты) возможность передать пользовательские валидаторы, которые будут вызываться во время работы дескриптора.

#### ExtendMeta

У *django model* есть `class Meta`, который устанавливает валидацию/настройки распространяющиеся на всю модель, в свою очередь у `extend field` есть `ExtendMeta` распостраняющийся на все `ExtendField` используемые в модели.

```
from extends import TranslatedField, ExtendMetaBase
from extends.opportunity import get_translator

class Question(models.Model):

    question = TranslatedField(
        models.CharField(_("question"), max_length=200),
        auto=([], []),
    )

    class ExtendMeta(ExtendMetaBase):
        override_query = True
        converter = {'question': get_translator}
```

`ExtendMeta` должен наследоваться от `ExtendMetaBase` и быть единственным потомком в одной моделе.

```
class ExtendMetaBase:

    override_query: bool = False
    converter: Callable[[str, str], str] | object | None = None
```

`override_query` - так как, расширение `Queryset` интерфейсов путем переопределения objects менеджера для сохранения единого интерфейса с django, может показаться излишним, его реализация активируется путём установки флага.

`converter` - тот же объект, что и в `auto` в сигнатуре TranslatedField, но распространяется на все указаные поля. Достаточно указать в одном из двух вариантов.

#### DeeplTranslator

ссылка на  [*Deepl API*](https://www.deepl.com/en/translator/q/es/tengo+hambre/en/I?utm_term=&utm_campaign=DE%7CPMAX%7CC%7CEnglish&utm_source=google&utm_medium=paid&hsa_acc=1083354268&hsa_cam=21575885684&hsa_grp=&hsa_ad=&hsa_src=x&hsa_tgt=&hsa_kw=&hsa_mt=&hsa_net=adwords&hsa_ver=3&gad_source=1&gclid=Cj0KCQiAlsy5BhDeARIsABRc6Zsq1wGg6YnxI-_2afXPq3HylcAJW5zhz5_NVLFGhW0wYZpFjlKjFSIaAkRFEALw_wcB) 

Для подключения *api* нужно получить `api key`, который при инициализации django будет помещен в переменные окружения, после достаточно использовать функцию `get_translator` для взаимодействия с транслятором.

```
class TextResultModel(BaseModel):

    text: str
    detected_source_lang: str


class DeeplTranslator(TranslatorBase, ApiHandler):
    pass

    def translate_text(self, src_text: str, target_lang: str) -> TextResultModel:
        pass
```

единственный внешний интерфейс транслятора `translate_text` отправляет запрос к deepl api и возвращает pydantic `TextResultModel`

### 5. Dev запуск и тестирование. <a id="dev"></a>
- Установить [poetry](https://python-poetry.org/) если не установлен на локальную машину.
- Стянуть репозиторий __ssh__: ```git clone git@github.com:zaritskiiAA/django-extend-fields.git```
- стянуть зависимости и развернуть venv bash: ```poetry install```
- в директории с `manage.py` выполнить миграции bash: `poetry run python manage.py migrate`
- для локального запуска bash: `poetry run python manage.py run`
- для запуска тестов bash: `poetry run pytest`
