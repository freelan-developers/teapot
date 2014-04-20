"""
A base class for object that have a signature.
"""

import hashlib


class SignableObject(object):

    """
    A base, signable object.
    """

    signature_fields = tuple()

    def __init__(self, *args, **kwargs):
        """
        Get the signable object instance.
        """
        super(SignableObject, self).__init__()

        self.hash = hashlib.sha1

    def get_signature_for(self, value):
        """
        Get the signature for a given value.
        """

        if isinstance(value, SignableObject):
            return value.signature

        m = self.hash()

        if isinstance(value, (list, tuple, set)):
            m.update('begin_list')
            map(m.update, map(self.get_signature_for, value))
            m.update('end_list')
        elif isinstance(value, dict):
            m.update('begin_dict')
            for key, value in value.iteritems():
                m.update(self.get_signature_for(key))
                m.update(self.get_signature_for(value))
            m.update('end_dict')
        elif value is None:
            m.update('none_value')
        elif value is True:
            m.update('true_value')
        elif value is False:
            m.update('false_value')
        else:
            m.update('begin_value')
            m.update(str(value))
            m.update('end_value')

        return m.hexdigest()

    @property
    def signature(self):
        return self.get_signature_for(map(
            lambda field: getattr(self, field),
            self.signature_fields
        ))
