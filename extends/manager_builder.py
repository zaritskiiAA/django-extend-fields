import inspect
from typing import Any
from functools import wraps

from django.db.models.manager import Manager


class TranslatedManagerWorkPiece:

    def update(self: Manager, **kwargs) -> int:
        translated_data, rest_data, desc = self._prepare_data(**kwargs)

        # You need to explicitly pass the type and object to "super" signature.
        # If do not, python by default take type from workpiece class.
        final_call = super(self.__class__, self).update

        return desc.proxy_from_orm(
            translated_data,
            final_call,
            **rest_data,
        )

    def _prepare_data(self: Manager, *args, **kwargs) -> dict[str, str] | dict[str, Any]:

        model_cls = self.model
        descriptors = model_cls._meta.extend_descriptor
        filter_args, filter_kwargs = [], {}

        for name, desc in descriptors.items():
            if name in kwargs:
                if hasattr(desc, 'auto'):
                    # TODO: заготовка к авто-траслитированию.
                    pass
                else:
                    filter_kwargs[desc.to_attribute(name)] = kwargs.pop(name)

        return filter_kwargs, kwargs, desc

    @classmethod
    def get_override_workpiece_methods(cls) -> dict:

        def create_method(name, method):

            @wraps(method)
            def override_method(self, *args, **kwargs):
                return getattr(cls, name)(self, *args, **kwargs)

            return override_method

        override_methods = {}
        for name, method in inspect.getmembers(
            cls,
            predicate=inspect.isfunction,
        ):
            override_methods[name] = create_method(name, method)
        return override_methods


class ManagerBuilder:

    workpiece_manager = TranslatedManagerWorkPiece

    def create_manager(self, src_manager: Manager) -> Manager:
        return type(
            'TranslatedManager',
            (src_manager.__class__,),
            {
                **self.workpiece_manager.get_override_workpiece_methods(),
            },
        )
