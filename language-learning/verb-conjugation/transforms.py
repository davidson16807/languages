
class HtmlPersonPositioning:
    def __init__(self):
        pass
    def farleft(self, person):
        return f'''<span style='position:relative; left:0.22em; top:0.2em;'>{person}</span>'''
    def left(self, person):
        return f'''<span style='position:relative; left:0.4em; top:0.2em;'>{person}</span>'''
    def center(self, person):
        return f'''{person}'''
    def right(self, person):
        return f'''<span style='position:relative; right:0.4em; top:0.2em;'>{person}</span>'''

class HtmlGesturePositioning:
    def __init__(self):
        pass
    def lowered(self, hand): 
        return f'''<span style='font-size: 50%; display: inline-block; width:0; position:relative; left:0.3em; top:0.8em;'>{hand}</span>'''
    def raised(self, hand): 
        return f'''<span style='font-size: 50%; display: inline-block; width:0; position:relative; right:0.6em; bottom:0.7em;'>{hand}</span>'''
    def overhead(self, hand): 
        return f'''<span style='display: inline-block; width:0; position:relative; bottom:0.8em;'>{hand}</span>'''
    def chestlevel(self, hand): 
        return f'''<span style='font-size: 50%; display: inline-block; width:0; position:relative; right:0.7em; top:0em;'>{hand}</span>'''
    def background(self, hand): 
        return f'''<span style='font-size: 50%; display: inline-block; width:0; position:relative; right:1em; bottom:0.9em; z-index:-1'>{hand}</span>'''

class HtmlTextTransform:
    def __init__(self):
        pass
    def mirror(self, emoji):
        return f'''<span style='display: inline-block; transform: scale(-1,1)'>{emoji}</span>'''
    def flip(self, emoji):
        return f'''<span style='display: inline-block; transform: scale(1,-1)'>{emoji}</span>'''

class HtmlNumberTransform:
    def __init__(self, htmlPersonPositioning):
        self.person = htmlPersonPositioning
    def singular(self, a): 
        return a
    def dual(self, a,b): 
        return f'''{self.person.left(a)}{self.person.center(b)}'''
    def plural(self, a,b,c): 
        return f'''{self.person.left(a)}{self.person.center(b)}{self.person.right(c)}'''
    def dual_inclusive(self, a,b): 
        return f'''{self.person.farleft(a)}{self.person.center(b)}'''
    def plural_inclusive(self, a,b,c): 
        return f'''{self.person.farleft(a)}{self.person.center(b)}{self.person.right(c)}'''

class HtmlTenseTransform:
    def __init__(self):
        pass
    def present(self, scene): 
        return f'''{scene}'''
    def past(self, scene): 
        return f'''<span style='filter: sepia(0.8)  drop-shadow(0px 0px 5px black)'>{scene}</span>'''
    def future(self, scene): 
        return f'''<span style='filter: blur(1px) drop-shadow(0px 0px 5px black)'>{scene}</span>'''

class HtmlAspectTransform:
    def __init__(self):
        pass
    def imperfect(self, scene): 
        return f'''{scene}<progress style='width:1em; height:0.7em; position:relative; top:0.5em; right:0.3em;' max='10' value='7'></progress>'''
    def perfect(self, scene): 
        return f'''{scene}<progress style='width:1em; height:0.7em; position:relative; top:0.5em; right:0.3em;' max='10' value='10'></progress>'''
    def aorist(self, scene): 
        return f'''{scene}'''
    def perfect_progressive(self, scene): 
        return f'''<span style='filter: sepia(0.3) drop-shadow(0px 0px 2px black)'>{scene}<progress style='width:1em; height:0.7em; position:relative; top:0.5em; right:0.3em;' max='10' value='10'></progress></span>'''

class HtmlBubble:
    def __init__(self):
        pass
    def affirmative(self, scene): 
        return f'''<div><span style='border-radius: 0.5em; padding: 0.6em; background:#ddd; '>{scene}</span></div>'''
    def negative(self, scene): 
        return f'''<div><span style='border-radius: 0.5em; padding: 0.6em; background: linear-gradient(to left top, #ddd 47%, red 48%, red 52%, #ddd 53%); border-style: solid; border-color:red; border-width:6px;'>{scene}</span></div>'''
    def box(self, scene):
        return f"<span style='border-radius: 0.5em; padding: 0.4em; border-style: solid; border-color:grey; border-width:3px;'>{scene}</span>"
