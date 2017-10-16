from ldap3 import Server, Connection, AUTH_SIMPLE, STRATEGY_SYNC, ALL, SUBTREE


class Ldap():

    def __init__(self):
        self.host = '10.100.0.130'
        self.user_dn = 'cn=admin,dc=mariana,dc=com'
        self.pwd = '12345'
        s = Server(self.host, get_info=ALL)
        self.c = Connection(
            s,
            authentication=AUTH_SIMPLE,
            user=self.user_dn,
            password=self.pwd,
            check_names=True,
            lazy=False,
            client_strategy=STRATEGY_SYNC,
            raise_exceptions=False)
        self.c.open()

    def list_ou(self):

        entry_list = self.c.extend.standard.paged_search(
            search_base='dc=mariana,dc=com',
            search_filter='(objectClass=organizationalUnit)',
            search_scope=SUBTREE,
            attributes=['ou'],
            paged_size=5,
            generator=False
        )

        user = []
        for entry in entry_list:
            user.append(entry['attributes'])
        return user

    def list_users(self):

        entry_list = self.c.extend.standard.paged_search(
            search_base='dc=mariana,dc=com',
            search_filter='(objectClass=inetOrgPerson)',
            search_scope=SUBTREE,
            attributes=[
                'uid',
                'cn',
                'givenName',
                'mail',
                'userPassword',
                'sn',
                'ou'],
            paged_size=5,
            generator=False)
        user = []
        for entry in entry_list:
            user.append(entry['attributes'])
        return user


if __name__ == '__main__':
    l = Ldap()
    print(l.list_ou())
