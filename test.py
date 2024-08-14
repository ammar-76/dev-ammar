import re
#getply("teakwood 40x40 8ply")
def getPly(s):
    # search by regular expression 
    # d = catches any decimal (0,9)
    # \s = matches zero or more (spaces, tabs, newlines, etc.).
    # ply = matches the literal string "ply"
    # this whole procces will apply upon the string s 
    print(s)
    print(s)
    print(s)
    matches=re.search(r'\b(\d+)\s*ply\b', s, re.IGNORECASE)
    # if there is any matches: 
    print(matches[1])
    if matches: # if the list of matches is not empty , in other words there is matches : 
        # matches[0] = #ply 
        # matches[1] = # -> number besie the ply
        size= int(matches[1]) 
        print(size)
        if size in (4,6,8): # if the # beside the ply one of these numbers 
            return size 
        else:
            return None

print(getPly("teakwood 40x40 8ply"))