#!/usr/bin/env python
# coding=utf-8

import six


class ChoiceMeta(type):

    def __new__(mcs, name, bases, attrs):

        choices = []
        values = []
        labels = []

        for field, value in attrs.items():

            if field.isupper():
                attrs[field] = value[0]
                values.append(value[0])
                labels.append(value[1])
                choices.append(value)

        attrs['CHOICES'] = choices
        attrs['KEY_LABELS'] = dict(choices)
        attrs['VALUES'] = values
        attrs['LABELS'] = labels

        return super(ChoiceMeta, mcs).__new__(mcs, name, bases, attrs)


class Choice(six.with_metaclass(ChoiceMeta)):

    @classmethod
    def get_label(cls, key, default=None):
        return cls.KEY_LABELS.get(key, default)
