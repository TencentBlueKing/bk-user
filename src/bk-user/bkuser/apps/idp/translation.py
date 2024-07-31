from modeltranslation.translator import TranslationOptions, translator

from .models import IdpPlugin


class IdpPluginTranslationOptions(TranslationOptions):
    fields = (
        "name",
        "description",
    )


translator.register(IdpPlugin, IdpPluginTranslationOptions)
