from modeltranslation.translator import TranslationOptions, translator

from .models import UserBuiltinField


class UserBuiltinFieldTranslationOptions(TranslationOptions):
    fields = ("display_name",)


translator.register(UserBuiltinField, UserBuiltinFieldTranslationOptions)
