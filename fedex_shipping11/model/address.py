import re

class Address(object):
    def __init__(self, name, address, address2, city, state_code, zip, country_code, phone='', email='', company_name='', country='', is_residence=True):
        self.company_name = company_name or ''
        self.name = name or ''
        self.address1 = address or ''
        self.address2 = address2 or ''
        self.city = city or ''
        self.state_code = state_code or ''
        self.zip = str(zip) if zip else ''
        self.country_code = country_code or ''
        self.country = country or ''
        self.phone = re.sub('[^0-9]*', '', str(phone)) if phone else ''
        self.email = email or ''
        self.is_residence = is_residence or False

    def __eq__(self, other):
        return vars(self) == vars(other)

    def __repr__(self):
        return (self.company_name, self.name, self.address1 , self.address2, self.city, self.state_code, self.zip, self.country_code, self.phone, self.email)

