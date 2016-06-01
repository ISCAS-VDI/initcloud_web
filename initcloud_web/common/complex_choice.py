#-*- coding=utf-8 -*-

import six

class ComplexChoiceMeta(type):

    def __new__(cls, name, bases, attrs):
        choices = {}
        for key, value in attrs.items():
            if key.isupper() and key.endswith("_CHOICE"):
                label = key[:len("_CHOICE")*-1]
                choices[label] = value
                del attrs[key]

        django_choices, value_labels, stable, unstable = [], [], [], []
        display = {}
        default = None

        for label, value in choices.items():
            display[value["value"]] = value["lable"]
            django_choices.append((value["value"], value["lable"]))

            if value.get("is_stable", True):
                stable.append(value["value"])
            else:
                unstable.append(value["value"])

            if value.get("is_default", False):
                default = value["value"]

            attrs[label] = value["value"]
            value_labels.append((value["value"], label))

        attrs["CHOICES"] = tuple(django_choices)
        attrs["VALUE_LABELS"] = tuple(value_labels)
        attrs["STABLE"] = stable
        attrs["UNSTABLE"] = unstable
        attrs["DEFAULT"] = default
        attrs["DISPLAY"] = display

        return super(ComplexChoiceMeta, cls).__new__(cls, name, bases, attrs)



class ComplexChoice(six.with_metaclass(ComplexChoiceMeta)):

    @classmethod
    def get_display(cls, key, default='N/A'):
        return cls.DISPLAY.get(key, default)
