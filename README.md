# ImageFapper
a Python class to download ImageFap.com galleries

Easy to use: 

instancesize the class by:

i = ImageFapper("pokemon kotone", root="/root")

the string as parameter in the construction method is the keyword you wanna search in the ImageFap.com

i.stage1()

is the method to collect ALL galleries link to the database

i.stage2()

will download ONE gallery under the root dir specified in the construction method

i.processLink(link)

will directly download all pics in the given gallery link, no database operations
