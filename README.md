# towerDefenseTest

A fun little video game in Python. Because unity is slow. Below is the premise! hope y'all like it :)


>It is Christmas Eve, one year since the war.
>
>One year since Santa Claus declared all of North America to be on the naughty list. That night, city after city was destroyed by nuclear hellfire. Humanity retreated in the face of this unstoppable threat, regrouping in the last stronghold, the citadel of Denver. It is the last hope of North America. The last few airbases are on high alert, ready to defend at any moment, at any cost.
>
>It is Christmas Eve. Denver sleeps uneasily under a blackout. Deep under Denver, the remnants of the North Warning System detect the unmistakeable radar signatures: Santa's sleighs are moving again.


## progress log, '25
#### Jul 29 - v0.0.1 'Voodoo'
- A lot of the preliminary art is in place. 
- So far Santa's sleigh-bombers are spawned via spacebar. 
- Clicking on airbases will spawn an interceptor. 

TODO - rework collisions?
TODO - make rotations work better?
TODO - game loop currently doesn't exist. Not really much of a game right now.

#### Jul 30 - v0.0.1b
- Bombers spawn in waves, waves stop when you run out of HP.

TODO - rework interceptors so they can take out more than one plane at a time?
TODO - restart game function
#### Aug 05 - v0.0.2 'DeltaDart'
- Interceptors will now retarget if their original target is gone and they have enough ammo.
- Interceptors now have more ammunition and will take out 2 sleighs before returning.
- Game now restarts when you press any key on losing.
- initial implement of tactical points for buying stuff. Can't buy anything yet.

TODO - WOW, rotations are really messed up. Not only are they spinning totally the wrong way they may be getting further away from the actual sprite rect? - fix ASAP!!!
TODO - Limit to 2 interceptors in the air at any time from an airbase.
TODO - open stores letting you buy more planes. 
#### XXX ?? - v0.0.3 - 'Republic'
#### XXX ?? - v0.0.4 - 'Starfighter'

