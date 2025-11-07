# Translation Files

This directory contains translation files for the Icosa Gallery application.

## Supported Languages

- Spanish (es)
- French (fr)
- German (de)
- Japanese (ja)
- Simplified Chinese (zh_Hans)

## Generating Translation Files

To extract all translatable strings and create/update `.po` files, run:

```bash
cd /home/user/icosa-gallery-test/django
python manage.py makemessages -l es -l fr -l de -l ja -l zh_Hans --ignore=venv --ignore=node_modules
```

This will create `.po` files in each language directory under `locale/{language}/LC_MESSAGES/django.po`.

## Compiling Translation Files

After translating the strings in the `.po` files, compile them to `.mo` files:

```bash
python manage.py compilemessages
```

## Translation Workflow

1. **Extract strings**: Run `makemessages` to extract all translatable strings from Python code and templates
2. **Translate**: Open the `.po` files in each language directory and translate the `msgstr` fields
3. **Compile**: Run `compilemessages` to compile the translations into binary `.mo` files
4. **Test**: Change your browser language or add `?language=es` to the URL to test translations
5. **Repeat**: As you add new features, re-run `makemessages` to extract new strings

## Translation Tools

You can use various tools to edit `.po` files:
- **Poedit**: GUI application for editing translations
- **Online**: Weblate, Transifex, or other translation platforms
- **Text editor**: Any text editor works for simple edits

## Notes

- Always run `makemessages` from the Django project root
- The `--ignore` flags prevent extracting strings from dependencies
- Translation files are in UTF-8 encoding
- After updating translations, always run `compilemessages` and restart the server
