def words(file):
    with open(file) as file:
        for line in file:
            for word in line.split():
                word = word.lower().strip('.,:;!?-')
                if word:
                    yield word
