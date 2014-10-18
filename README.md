#Critter API

API stands for Application Programmer Interface, which means it's the
way the application programmer (you) gets at the framework, service or
library providing the API—in other words, an API answers the question
*“How in the heck do you drive this thing?”*

APIs are seldom static; new version of the software often change the
API and thus you may have to change your code.  Nice API designers
will at least warn you about things that may go away (by marking them
as “deprecated”), known to be buggy, etc. and will avoid changing
things in surprising ways.

###Events

The Critter API presently supports three event types:

* `on_collision(self,dir,other,senses)`

    Called when your critter is involved in a collision.  Passes in four parameters:

    - `self` – this is your critter
    - `dir` – the compass direction to the thing that you collided with ***deprecated***
    - `other` – the thing you collided with
    - `senses` – what you can sense (see the next section for details)

* `on_attack(self,dir,attacker,senses)`

    Never called, since there's presently no way for critters to attack
    each other and nothing else in the world that could attack them.

* `on_tick(self,senses)`

    Called once a “tick” (about ten times a second).  This is the main
    callback that lets your critter decide what to do.  As above, <self> is
    set to your critter and <senses> provides the incoming data.

* ***More callbacks may be added in the future***


###Incoming data (to your code)

All callbacks provide the current information from your critter's
senses as a dictionary.  Presently, it contains data from six sense
organs:

* `senses['sight']` – A set of tuples: (color,distance,direction,width,change)
* `senses['smell']` – A set of tuples: (strength,smell,change) ***presently buggy***
* `senses['hearing']` – A set of tuples: (sound, relative direction, how
long ago) ***should probably include loudness***
* `senses['taste']` – A set of tastes
* `senses['body']` – A body senses tuple: (moving, speed, age, health)
* `sense['gps']` – Your critter's current location  ***deprecated***
* `sense['compass']` – The direction your critter is facing ***deprecated***
* ***More senses should be added (e.g. movement, health, hunger, etc.)***

###Control commands (from your code)

Callbacks can return a string telling your critter's body what to do.
If no command is given, most callbacks presently assume `“Pass”` (the
main exception being on_collision, which defaults to `"Eat"` if the collision
was with Food).  Presently supported commands are:


* `"Stop"` – Stop moving (actually, just slow waaaay down).

* `"Go"` – Resume moving at a normal speed.

* `"Turn X"` – Turn a given amount.

    If X is negative, turns left; if X is positive, turns right.  If X
    is zero, does nothing.  There's a limit to how far you can turn in
    one tick; trying to turn further than this just turns the maximum
    amount.

* `"Accelerate X"` – Accelerate by the given ratio.

    If X is less than 1.0, slows down.  You can only go so fast;
    attempting to accelerate past the maximum speed does nothing.

* `"Attack"` – ***unimplemented***

* `"Eat"` – Eat if there's anything edible under you, otherwise does nothing.

* `“Pass”` – Do nothing (continues moving forward unless stopped).

* ***More control commands may be added in the future***
