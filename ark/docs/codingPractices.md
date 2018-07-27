- lowerCamelCase variable names
- 4 space tabs
	- that's actual tabs, not 4 spaces
- brackets always on a separate line
```
	if (foo == 'bar')
	{
		print 'sup'
		return 12
	}
```
- skip brackets for single line if's
```
	if (foo == 'bar')
		print 'sup'
```
- exception to this rule if the else needs brackets
```
	if (foo == 'bar')
	{
		print 'sup'
	}
	else
	{
		print 'hey'
		foo = bar
	}
```
- no single line if's, ex: ```if (err) throw err```
- use single quotes whenever possible
```
	'someString'
```
- write self-documenting code
- use full, descriptive variable names
	- avoid abbreviations
	- avoid single letters
```
	# bad
	p = getPath()
	i = countFiles(p)

	# good
	path = getPath()
	fileCount = countFiles(p)
```
- no magic numbers, assign them to a variable so they document themselves
- don't write confusing code
	- solve problems in the simple, straightforward ways
	- avoid complex one-liners
	- avoid obscure methods and practices
- space not speed
	- code is written once and read many times
- spread stuff out and format it nicely
- unit testing
	- write tests before you write code
	- tests inform how the code you're about to write should work
	- write a test for any bugs you find so they don't crop up again
- for function calls and definitions, no space after the opening parenthesis, spaces after commas
```
	setPosition(200, 400, 800)
```
- write docstrings once a function is working
- document confusing code as you go (if it can't be avoided)
- great resource on common pitfalls: [QT API Design Principles](http://wiki.qt.io/API-Design-Principles#API_Semantics_and_Documentation)
- nice [project setup guide for Python](http://infinitemonkeycorps.net/docs/pph/#setup-py) (applicable to other languages as well)
