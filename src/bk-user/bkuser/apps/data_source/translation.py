# translation.py

from modeltranslation.translator import TranslationOptions, translator

from .models import DataSourcePlugin


class DataSourcePluginTranslationOptions(TranslationOptions):
    fields = (
        "name",
        "description",
    )  # 需要翻译的字段


translator.register(DataSourcePlugin, DataSourcePluginTranslationOptions)
