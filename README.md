Scrabble solver, written in Python with OOP
-------------------------------------------

Letter distribution:
	A=9	D=5	G=3	J=1	M=2	P=2	S=5	V=2	Y=2
	B=2	E=13	H=4	K=1	N=5	Q=1	T=7	W=2	Z=1
	C=2	F=2	I=8	L=4	O=8	R=6	U=4	X=1	*=2

Letter values:
	A=1	D=2	G=3	J=10	M=4	P=4	S=1	V=5	Y=3
	B=4	E=1	H=3	K=5	N=2	Q=10	T=1	W=4	Z=10
	C=4	F=4	I=1	L=2	O=1	R=1	U=2	X=8	*=0

DONE:
* Horizontal scan , without hooking - i.e. where you play one letter
horizontally to form a word whilst also playing letters vertically to form
another word) - supporting hooking requires a single vertical scan to be conducted
in the case that only a single letter is played.

* The Horizontal scan relies upon the splitRow method which splits a row into
substrings separated by white space and returns the relevant information.
Construction of a vertical scan method will require an analogous 'splitColumn'
method.

* Have commented on splitRow, and begun looking at boardScan but cannot proceed without
internet access as I cannot look up the libraries.

* Planned out a method for splitColumn that will give the same results as splitRow but hopefully
be more elegant via using the re library - cannot code without internet.

TODO:
* As mentioned above first an analogous column method to splitRow must be constructed.

* This will then allow for the construction of the vertical scan method, which can be
used to support hooking in the horizontal scan and also completes the scanning part
of the code, in order to support hooking a single horizontal scan would have to be called
in the case of a single letter played vertically

* Because of the requirements of hooking, and to make the code more understandable, it
seems to be strongly advisable to break the horizontal scan and vertical scan into 2 methods,
which are then called by the boardScan method.

* Finally the splitRow method should probably be improved upon to make it clearer via
additional comments and refactoring to explain what is going on, this would also make the
construction of the analogous column method far easier.

* That appears to be all that is necessary to have a basic working solver - I would strongly
recommend that once such a solver is complete the python debugger/profiler is used to check
for bottlenecks and any obvious optimisation is conducted

* The scoring function also needs to be written (this looks like it might already be done...
is it finished??) although that shouldn't be too difficult?
Just remember the special cases like the 35 point bonus for using all the letters, and
the special tiles etc., we also need to handle blank tiles which is a difficulty...

* There is a blank function called checkWordplay in the code, but I don't see why it is necessary
as surely splitRow/column would return the number of spaces available and that can be used to determine
whether placement is possible? But perhaps placing such a check in it's own method is better I don't know.

* Also need to handle the special case that it is the first turn (i.e. the board is blank,
 have to place a tile on the centre?), but this doesn't seem like it should be too hard...