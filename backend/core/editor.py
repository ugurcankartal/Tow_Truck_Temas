"""django-prose-editor (TipTap) alan yapılandırmaları."""

HERO_INTRO_TITLE_EXTENSIONS = {
    'Bold': True,
    'Italic': True,
    'HardBreak': True,
}

HERO_INTRO_BODY_EXTENSIONS = {
    'Bold': True,
    'Italic': True,
    'BulletList': True,
    'OrderedList': True,
    'ListItem': True,
    'Link': True,
    'HardBreak': True,
}

SHOWCASE_SECTION_DESCRIPTION_EXTENSIONS = HERO_INTRO_BODY_EXTENSIONS
