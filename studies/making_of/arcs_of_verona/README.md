## Generative Study: Arcs Of Verona

For several years I was watching my wife drawing sketches and studies to grow as an artist.
Then suddenly I had the idea to try the same by myself. But using the power of pure code instead of brushes and pencils.

So, I called this format "Generative Studies", wrote a brief Concept for myself, and started with my first study.

The original photo I tried to reproduce was an arcade somewhere in the city of Verona.
Its beautiful colors and magnificent architecture was an inspiration for me during the whole process.

### Phase 1: Main Wall / Arc Form

![Arcs Of Verona (Phase 1)](/studies/making_of/arcs_of_verona/img/arcs_of_verona_phase01.png)

I started with the things in the foreground. The main wall and the first arc of the same color.

The wall consists of bricks, but they are not identical. They differs in color and a brick's width also differs from column to column. So, I generated a perfect grid for future bricks, then randomly shifted each vertical line a bit. To achieve more natural-looking result, I used Gauss distribution through the whole study. For bricks' colors, I picked up two base values (lightest and darkest shades), then blended each brick's color between them using the same Gauss distribution.

The arc form was the trickest part in the study. I meditated on the original photo for amount of time just to end up with the fact I have no idea how to reproduce it. So, I opened a photo in my favorite editor, and draw several lines through the gaps between the bricks, just out of interest. The result astonished me immediately. Lines for the first quater are all intersecting at the same point, right in the "center" of the arc. For the second quarter, lines are intersecting at the other point... roughly twice as large as the first lines.

With that two facts, it became pretty clear for me how to reproduce the arc's contour. Let simulate it with two circular paths, first with the radius R (half arc's width), second with the radius 2R (arc's width). Herewith, last point of the first path, and the first point of the second path should be the same.

The rest was automatic. I just generated a smaller path with the same form, and drew bricks between this two using the same random width/color approach as for the main wall.

### Phase 2: Perspective / Floor Pattern

![Arcs Of Verona (Phase 2)](/studies/making_of/arcs_of_verona/img/arcs_of_verona_phase02.png)

### Phase 3: Reflections / Far Wall

![Arcs Of Verona (Phase 3)](/studies/making_of/arcs_of_verona/img/arcs_of_verona_phase03.png)

### Phase 4: Bricks' Depth / Corrected Reflections

![Arcs Of Verona (Phase 4)](/studies/making_of/arcs_of_verona/img/arcs_of_verona_phase04.png)

### Phase 5: Basic Lighting

![Arcs Of Verona (Phase 5)](/studies/making_of/arcs_of_verona/img/arcs_of_verona_phase05.png)

### Phase 6: Advanced Lighting

![Arcs Of Verona (Phase 6)](/studies/making_of/arcs_of_verona/img/arcs_of_verona_phase06.png)

### Phase 7: Ceiling

![Arcs Of Verona (Phase 7)](/studies/making_of/arcs_of_verona/img/arcs_of_verona_phase07.png)

### Phase 8: Altar / Far Arc

![Arcs Of Verona (Phase 8)](/studies/making_of/arcs_of_verona/img/arcs_of_verona_phase08.png)

### Phase 9: Lamps

![Arcs Of Verona (Phase 9)](/studies/making_of/arcs_of_verona/img/arcs_of_verona_phase09.png)

### Phase 10: Additional Details

![Arcs Of Verona (Phase 10)](/studies/making_of/arcs_of_verona/img/arcs_of_verona_phase10.png)
