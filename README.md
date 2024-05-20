# Galaxy Tool Shed
This project stores our custom Finkbeiner Lab Galaxy tools and exposes them to Galaxy as an additional Tool Shed repository. See Galaxy's guide to [adding tools](https://galaxyproject.org/admin/tools/add-tool-from-toolshed-tutorial/) for more info.


## Structure of this project
Galaxy_Tool_Shed/
├── tool1/
│   ├── tool1.xml
│   ├── tool1.py
│   └── test-data/
├── tool2/
│   ├── tool2.xml
│   ├── tool2.py
│   └── test-data/
└── README.md


## Tell Galaxy about our Tool Shed
This ToolShed will be pulled into Galaxy by creating/modifying the Galaxy's `config/tool_sheds_conf.xml` with the following:
```
<?xml version="1.0"?>
<tool_sheds>
    <tool_shed name="FinkbeinerToolShed" url="https://github.com/finkbeiner-lab/Galaxy_Tool_Shed" />
</tool_sheds>
```

Then Galaxy has to know to import this tool shed config file. We can create/modify the following to `config/galaxy.yml` to do so:
```
tool_sheds_config_file: config/tool_sheds_conf.xml
```

## Install the Tool
Tools are not usually installed by default just because they exist in a Tool Shed that Galaxy knows about. There are many Galaxy Tool Sheds, with thousands of available tools. So if your tool isn't showing up, it probably needs to be installed in Galaxy through the admin interface.
=======
This project stores our custom Finkbeiner Lab Galaxy tools and exposes them to Galaxy as an additional ToolShed repository. See Galaxy's guide to [adding tools](https://galaxyproject.org/admin/tools/add-tool-from-toolshed-tutorial/) for more info.

# Structure
There is an outer ToolShed repository that contains references to each tool's individual repository. This repository composition structure is driven by the recommended approach from the Galaxy developers.
