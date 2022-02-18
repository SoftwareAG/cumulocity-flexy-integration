<p align="right">08/02/2022</p>

# Quick Start Guide - Flexy Registration

__What is the funcionality of the *Flexy Registration* tool?__
The tool *Flexy Registration* allows a quick and easly migration of Ewon Flexy devices from the cloud solution *Talk2M* by HMS Networks to Cumulocity IoT.

__Who can use the registration tool?__ 

Everyone who uses Ewon Flexy devices from *HMS Networks* and their cloud solution "Talk2M".

__Who can use the registration tool?__

Registration:
Talk2M Registered means that the device is stored in the Talk2M Platform and has an EWON Id. If not, then the device was created manually with the serial number.

Cumulocity registered means that the device has been registered and created on the tenant and has an externalID either ewonId or serial number and the device credentials have been created (we don't see here whether the device took it and is "really" connected).


## Description


## Usage

### Installing

### Folder structure

### Setup generic data
### Creating chapters

#### Insert a table

Use markdown table, and use the `Table: <Your table description>` syntax to add
a caption:

```md
| Index | Name |
| ----- | ---- |
| 0     | AAA  |
| 1     | BBB  |
| ...   | ...  |

Table: This is an example table.
```

If you want to reference a table, use LaTeX labels:

```md
Please, check Table /ref{example_table}.

| Index | Name |
| ----- | ---- |
| 0     | AAA  |
| 1     | BBB  |
| ...   | ...  |

Table: This is an example table.\label{example_table}
```

## References

- [Pandoc](http://pandoc.org/)
- [Pandoc Manual](http://pandoc.org/MANUAL.html)
- [Wikipedia: Markdown](http://wikipedia.org/wiki/Markdown)
