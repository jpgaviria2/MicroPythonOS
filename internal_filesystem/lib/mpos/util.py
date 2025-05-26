def urldecode(s):
    result = ""
    i = 0
    while i < len(s):
        if s[i] == '%':
            result += chr(int(s[i+1:i+3], 16))
            i += 3
        else:
            result += s[i]
            i += 1
    return result
