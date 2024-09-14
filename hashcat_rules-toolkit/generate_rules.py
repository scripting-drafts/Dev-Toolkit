'''2-7 NUMBERS RULES'''

with open('2-7.rules', 'w') as f:
    for line in range(2, 8):
        f.write(f'${line}\n')

    f.close()


'''ALPHABET RULES'''
# import string

# abc = list(string.ascii_lowercase)

# with open('abc.rules', 'w') as f:
#     for line in abc:
#         f.write(f'${line}\n')

#     f.close()