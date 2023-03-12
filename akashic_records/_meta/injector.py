import ast
import functools
import importlib.abc
import importlib.machinery

import inspect
from typing import Annotated

from sorcery import spell

from akashic_records._meta.dynamic_function import CodeBuilder
from akashic_records._meta.errors import ExhaustedAttemtpsError, MultiError


class Loader(importlib.abc.Loader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type_hint = True
        self.n = 3
        self.max_tokens = 512
        self.temperature = 0.2
        self.attempts = 5

    def create_module(self, spec):
        fake_func = type(
            spec.name,
            (object,),
            {
                "__init__": None,
            },
        )
        builder = CodeBuilder(self.n, self.temperature, self.max_tokens)
        dyn = None

        @spell
        @functools.wraps(fake_func)
        def dynamic_function(frame_info, *args, **kwargs):
            nonlocal dyn
            if not dyn:
                # TODO: Should I use the call line somewhere?
                # call_line = frame_info.get_source(frame_info.call)

                # TODO: is there another way to extract the type hint from the call?
                #       this is kinda jank
                statement = None
                for statement in frame_info.executing.statements:
                    break

                docstring_content = None
                return_type = inspect.Signature.empty
                if (
                    isinstance(statement, ast.AnnAssign)
                    and isinstance(statement.annotation, ast.Constant)
                    and isinstance(statement.annotation.value, str)
                ):
                    annotation = statement.annotation.value
                    docstring_content = inspect.cleandoc(annotation)
                elif (
                    isinstance(statement, ast.AnnAssign)
                    and isinstance(statement.annotation, ast.Subscript)
                    and statement.annotation.value.id == "Annotated"
                ):
                    if self.type_hint:
                        return_type = statement.annotation.slice.elts[0].id  # type: ignore
                    for annotation in statement.annotation.slice.elts[1:]:  # type: ignore
                        if isinstance(annotation, ast.Constant) and isinstance(
                            annotation.value, str
                        ):
                            docstring_content = inspect.cleandoc(annotation.value)
                            break

                parameters = [
                    inspect.Parameter(
                        # FIXME: When a constant is passed to a function, this name generation process fails
                        #          Workaround is to use keyword args
                        frame_info.get_source(arg) if frame_info.get_source(arg).isidentifier() else "p%d" % i,
                        annotation=type(value)
                        if self.type_hint
                        else inspect.Parameter.empty,
                        kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    )
                    for i, (arg, value) in enumerate(zip(frame_info.call.args, args))
                ]
                parameters.extend(
                    [
                        inspect.Parameter(
                            name,
                            annotation=type(value)
                            if self.type_hint
                            else inspect.Parameter.empty,
                            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        )
                        for name, value in kwargs.items()
                    ]
                )
                sig = inspect.Signature(parameters, return_annotation=return_type)
                attempt = self.attempts
                errors = MultiError()
                # Intentionally brittle check to allow for unlimited attempts using any negative number
                while attempt != 0:
                    attempt -= 1
                    # TODO: builder.build_class if spec.name[0] is a capital letter
                    for func in builder.build_function(
                        spec.name, sig, docstring_content
                    ):
                        try:
                            result = func(*args, **kwargs)
                            dyn = func
                            return result
                        except Exception as e:
                            errors.append(e)
                            # TODO: log
                            pass
                raise ExhaustedAttemtpsError(
                    f"Was not able to generate valid {spec.name} function after {self.attempts} attempts.\n"
                    "If implementations are cut off early consider increasing max_tokens"
                ) from errors

            return dyn(*args, **kwargs)

        return dynamic_function

    def exec_module(self, module):
        pass


class Finder:
    _COMMON_PREFIX = "akashic_records."

    def __init__(self, loader):
        self._loader = loader

    def find_spec(self, fullname, path, target=None):
        if fullname.startswith(self._COMMON_PREFIX):
            name = fullname[len(self._COMMON_PREFIX) :]
            return self._gen_spec(name)

    def _gen_spec(self, fullname):
        return importlib.machinery.ModuleSpec(fullname, self._loader)
