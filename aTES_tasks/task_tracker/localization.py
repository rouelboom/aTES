"""
Localization utilities
"""
import gettext

gettext.install('task-tracker')


def set_lang(lang, locale_path: str = None):
    """
    Change language on the fly
    """
    t = gettext.translation('task-tracker', locale_path, languages=[lang], fallback=True)
    t.install()
