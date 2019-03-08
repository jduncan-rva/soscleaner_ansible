#!/usr/bin/python

# Copyright: (c) 2019, Jamie Duncan <jduncan@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {
    'metadata_version': '0.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: soscleaner

short_description: Ansible module to interact with SOSCleaner for data obfuscation

version_added: "2.7"

description:
    - "The soscleaner module interacts with the SOSCleaner library to add data obfuscation to workflows."

options:
    sosreport:
        description:
            - The sosreport to obfuscate using soscleaner
        required: true
    domains:
        description:
            - Additional domains to obfuscate in the sosreport
        required: false
    networks:
        description:
            - Additional networks to obfuscate in the sosreport
        required: false
    keywords:
        description:
            - Additional keywords to obfuscate in the sosreport
        required: false
    users:
        description:
            - Additional users to obfuscate in the sosreport
        required: false
    macs:
        description:
            - Additional MAC addresses to obfuscate in the sosreport
        required: false


extends_documentation_fragment:
    - azure

author:
    - Jamie Duncan (@jduncan-rva)
'''

EXAMPLES = '''
# Pass in a message
- name: Test with a message
  my_new_test_module:
    name: hello world

# pass in a message and have changed true
- name: Test with a message and changed output
  my_new_test_module:
    name: hello world
    new: true

# fail the module
'''

RETURN = '''
original_message:
    description: The original name param that was passed in
    type: str
message:
    description: The output message that the sample module generates
'''

from ansible.module_utils.basic import AnsibleModule
from soscleaner import SOSCleaner


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        sosreport=dict(type='path', required=True),
        domains=dict(type='list', required=False),
        networks=dict(type='list', required=False),
        users=dict(type='list', required=False),
        keywords=dict(type='list', required=False),
        loglevel=dict(choices=['INFO', 'WARNING', 'ERROR', 'CRITICAL', 'DEBUG'], default='INFO'),
        report_dir=dict(type='path', required=True, default='/tmp'),
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        sosreport_path='',
        obfuscated_report_path='',
        hostname_report='',
        domainname_report='',
        ip_report='',
        user_report='',
        mac_report='',
        keyword_report='',
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        return result

    cleaner = SOSCleaner()
    cleaner.quiet = True
    cleaner.loglevel = module.params['loglevel']
    cleaner.origin_path, cleaner.dir_path, cleaner.session, cleaner.logfile, cleaner.uuid = cleaner._prep_environment()
    cleaner._start_logging(cleaner.logfile)

    cleaner.clean_report(module.params, module.params['sosreport'])

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    result['sosreport_path'] = module.params['sosreport'],
    result['obfuscated_report_path'] = cleaner.report_dir,
    result['hostname_report'] = cleaner.hn_report,
    result['domainname_report'] = cleaner.dn_report,
    result['ip_report'] = cleaner.ip_report,
    result['user_report'] = cleaner.user_report,
    result['mac_report'] = cleaner.mac_report,
    result['keyword_report'] = cleaner.keyword_report,
    result['changed'] = True

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
