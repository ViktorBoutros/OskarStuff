
def any_in(s, words):
        for word in words:
            if word in s:
                return True
        return False
    
def all_in(s, words):
    for word in words:
        if word not in s:
            return False
    return True

