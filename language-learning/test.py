
from shorthands import ListParsing
from languages import ListProcessing, ListTools, Rule

parsing = ListParsing()
tools = ListTools()

original = parsing.parse('clause [rational [np the [n man]] [cloze v conjugated]] [np modifier]')

replacement = ListProcessing({
        'declined':   tools.replace(['animal']),
        'conjugated': tools.replace(['give']),
        'modifier':   tools.replace(['gift']),
        'adposition': tools.replace(['adp', '...']),
        'the':        tools.replace(['art', 'the']),
        'a':          tools.replace(['art', 'a']),
    }, 
)
replaced = replacement.process(original)

presets = {
    'rational': {'noun-form':'common', 'number':'singular'}
}

conversion = ListProcessing({
        **{tag:tools.rule() for tag in 'clause cloze art adp np vp n v'.split()},
        **{key:tools.grammemes(presets[key]) for key in 'rational possession inanimate'.split() if key in presets}
    }, 
)
converted = conversion.process(replaced)

print('original', original)
print('replaced', replaced)
print('converted', converted)

