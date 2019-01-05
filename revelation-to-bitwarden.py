#!/usr/bin/env python3
#
# revelation-to-bitwarden - Convert the Revelation password store XML exports to the Bitwarden JSON format
#
# Copyright 2019 Emanuele Aina <em@nerd.ocracy.org>
#
# SPDX-License-Identifier: MIT

import json
import os
import sys
import uuid
import xml.etree.ElementTree as ET

revelation_xml = sys.argv[1]

revelationdata = ET.parse(revelation_xml)
bitwarden = {
    'folders': [],
    'items': [],
}

def add_uri(item, uri):
    item['login']['uris'].append({'uri': uri})

def add_field(item, name, value):
    item['fields'].append({
        'name': name,
        'value': value,
        'type': 0,
    })

def process_entry(folder, entry):
    entry_type = entry.attrib['type']
    name = entry.findtext('name')
    description = entry.findtext('description')
    notes = entry.findtext('notes')
    
    if entry_type == 'folder':
        folder = {
            'id': str(uuid.uuid4()),
            'name': name,
        }
        bitwarden['folders'].append(folder)
        for subentry in entry.findall('entry'):
            process_entry(folder, subentry)
    else:
        generic_url = entry.findtext('./field[@id="generic-url"]')
        generic_username = entry.findtext('./field[@id="generic-username"]')
        generic_email = entry.findtext('./field[@id="generic-email"]')
        generic_password = entry.findtext('./field[@id="generic-password"]')
        generic_pin = entry.findtext('./field[@id="generic-pin"]')
        generic_hostname = entry.findtext('./field[@id="generic-hostname"]')
        generic_domain = entry.findtext('./field[@id="generic-domain"]')
        generic_certificate = entry.findtext('./field[@id="generic-certificate"]')
        generic_keyfile = entry.findtext('./field[@id="generic-keyfile"]')
        phone_phonenumber = entry.findtext('./field[@id="phone-phonenumber"]')
        
        item = {
            'id': str(uuid.uuid4()),
            'type': 1,
            'name': name,
            'notes': "{}\n\n{}".format(description, notes).strip(),
            'fields': [],
            'login': {
                'uris': [],
                'username': generic_username or generic_email,
                'password': generic_password or generic_pin,
            },
        }

        if generic_url:
            add_uri(item, generic_url)

        if folder:
            item['folderId'] = folder['id']

        if generic_email:
            add_field(item, 'Email', generic_email)

        if phone_phonenumber:
            add_field(item, 'Phone number', phone_phonenumber)

        if generic_keyfile:
            add_field(item, 'Keyfile', generic_keyfile)

        bitwarden['items'].append(item)

for entry in revelationdata.getroot():
    process_entry(None, entry)

print(json.dumps(bitwarden))
