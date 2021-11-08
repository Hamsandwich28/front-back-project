class User:
    __slots__ = ('_email', '_phash', '_lname', '_fname')

    null_hash = '0' * 256
    base_user = User('some@text.go', null_hash, 'LASTNAME', 'FIRSTNAME')

    @classmethod
    def get_base(cls):
        return cls.base_user

    def __init__(self, email, phash, lname, fname):
        self._email = email
        self._phash = phash
        self._lname = lname
        self._fname = fname

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        if not isinstance(email, str):
            raise TypeError(f'{email} должен быть строкой!')
        self._email = email

    @property
    def phash(self):
        return self._phash

    @phash.setter
    def phash(self, phash):
        if not isinstance(phash, bytearray) and len(phash) != 256:
            raise TypeError('Хэщ должен быть строкой бит!')
        self._phash = phash

    @property
    def lname(self):
        return self._lname

    @lname.setter
    def lname(self, lname):
        if not isinstance(lname, str):
            raise TypeError(f'{lname} должен быть строкой!')
        self._lname = lname

    @property
    def fname(self):
        return self._fname

    @fname.setter
    def fname(self, fname):
        if not isinstance(fname, str):
            raise TypeError(f'{fname} должен быть строкой!')
        self._fname = fname

    def __str__(self):
        return f'User <{self.lname} | {self.fname} | {self.email}>'

    def __repr__(self):
        return self.__str__()

