# CherryTree to Markdown
Convert CherryTree XML files that are not password protected to Markdown.

This converter handles most Markdown rules. However, when writing in CherryTree, you may need to adjust some text to ensure proper conversion. For example, you should leave a blank line before every list; otherwise, the list will be interpreted as normal text in Markdown viewers.

## TODO Later

Additionally, CherryTree includes a char_offset attribute in its XML for tables, images, and code blocks. This attribute is used to position these elements accurately. Currently, this converter does not support char_offset, so tables, images, and code blocks may appear in incorrect positions.
