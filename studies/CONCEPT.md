## Generative Studies Concept

Every artist do studies to understand the properties of natural
objects. Generative artists could adopt this approach too.

All you need is to pick up a realistic image and try to reproduce it
as close as possible (light, color, form, perspective and
composition), using only the power of code.

If it sounds too easy for you, there is an additional set of rules,
to avoid "cheating".

1. You should not use the original or any other images in your code.
2. Every color you use should be derived from a limited set of base
   colors that are extracted from the original image. Preferrable number
   of base colors is 5.
3. All coordinates you use should be derived from the width and height
   of your final image. No hardcoded coordinates are allowed.
4. Follow the code style for your language of choice, and leave
   detailed comments of what you are doing.
5. Try not to exceed N lines of code. N=500 is enough for Python/Cairo
   stack to keep your work detailed, but not overcomplicated.
6. Share the resulting code with a short summary of what did you
   learn, so others could learn from it too.

During your studies, you could write a small library of utility
functions that will do common tasks for you. Drawing primitives,
transforming colors and coordinates, building perspective, etc. Then,
you could re-use it in other studies.

And the good news, you could even re-use parts of the older studies in
the newer ones. Just build the whole studies ecosystem in a manner of
a package and they will grow in power with every new study complete.

Another point for the studies ecosystem is to keep all previous
studies working and producing correct images. For that, you could
write a unit-test suite, which will do all the dirty job for you.

And the last, have fun with a process. Do not let it throw you into
the abyss of formality. Use it for your inspiration and a good mood =)
