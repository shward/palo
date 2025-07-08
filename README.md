# palo

_A dumping ground for all the stuff Palo Alto **should** have built in... but didn’t._

This repo contains a growing collection of scripts, hacks, workarounds, and automation tools for dealing with Palo Alto Networks firewalls and Panorama. Most of these were written to:

- save time,
- reduce human error,
- make bulk changes easier,
- or just stop yelling at the screen during routine tasks.

If you've ever found yourself thinking “why isn’t this a built-in feature?”, buddy you’re in the right place.

---

##  What’s Inside? (or what's coming?!)

Scripts here may include (but are not limited to):

- **Address/Object Management**
  - Bulk tag updates
  - Object cleanup or tagging by pattern
- **Policy & Rulebase Tools**
  - Rule parsing
  - Rule expansion or documentation generation
- **Dynamic Address Group Utilities**
  - Tag audits
  - Membership extractors
- **Panorama Automation**
  - Device group and template introspection
  - Config backups in `set` format (for sane diffing!)
- **EDL and IOC Tools**
  - External list inspection
  - Quick match tools for IPs/domains against loaded EDLs
- **Logging & Debug Helpers**
  - Scripts to detect Cortex/CDL blackhole scenarios
  - Logging sanity checks
- **API Interaction**
  - XML and REST calls to make Panorama less terrible
- **CLI Wrappers**
  - Generate bulk delete commands
  - Parse or reformat Panorama CLI output

---

## Disclaimer

These scripts are sharp tools. Many interact directly with production firewalls and APIs. No warranties, no support, no safety nets. Test in staging, review the code, and use at your own risk.

Also: Palo Alto, if you're reading this — please hire someone to build literally any of this into the product.

---

##  Requirements

Most scripts are written in Python 3. Some use:

- `requests`
- `paramiko`
- `lxml`
- `argparse`
- your soul

A virtual environment (`venv`) is usually recommended. See individual script headers for specific requirements.

---

##  How to Use

Each script should include a `--help` flag. It also includes a "-h" flag which does the same thing if you're lazy. Most follow sane CLI conventions and include inline docs/snark.

```bash
python3 palo-edl-find.py --help

