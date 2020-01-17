#!/usr/bin/env python3

import argparse
import abmclient
import inspect

import sys, os
from model import Model

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'models'))

def load_model(name):
    module = __import__(name)

    all_classes = inspect.getmembers(module, inspect.isclass)
    model_class = [cls for x, cls in all_classes if issubclass(cls, Model)]
    return model_class[0]()

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='ABM Platform Python Client')
    ap.add_argument('model',
            metavar='MODEL',
            type=str,
            help='Model name')
    args = ap.parse_args()

    model = load_model(args.model)
    c = abmclient.ABMClient(model)
    c.start()
