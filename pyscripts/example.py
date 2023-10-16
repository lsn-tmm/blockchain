#!/usr/bin/env python

import hashlib


hash = hashlib.sha256('AMPM members'.encode()).hexdigest()
print(f"\nHello World {hash}", end='\n\n')
