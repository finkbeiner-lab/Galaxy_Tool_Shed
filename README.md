# Galaxy Tool Shed
This project stores our custom Finkbeiner Lab Galaxy tools and exposes them to Galaxy as an additional Tool Shed repository. See Galaxy's guide to [adding tools](https://galaxyproject.org/admin/tools/add-tool-from-toolshed-tutorial/) for more info.


## Structure of this project
In Galaxy, each tool is in its own "shed", the name given to a repository that contains a single tool. These "sheds" or "repositories" are contained within the ToolShed. Each shed is decoupled from the others, and has its own versioning, dependencies,and metadata. The structure of this project therefore follows the ToolShed structure defined by Galaxy.

```
Galaxy_Tool_Shed/  
├── tool_name/
│   ├── tool_name.xml
│   ├── tool_name.py
│   ├── test-data/
│   │   ├── test_input1.txt
│   │   └── expected_output1.txt
│   │   ├── test_input2.txt
│   │   └── expected_output2.txt
│   ├── README.rst
│   └── .shed.yml
├── tool_name/
│   ├── tool_name.xml
│   ├── tool_name.py
│   ├── test-data/
│   │   ├── test_input1.txt
│   │   └── expected_output1.txt
│   │   ├── test_input2.txt
│   │   └── expected_output2.txt
│   ├── README.rst
│   └── .shed.yml
└── README.md
```

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
This project stores our custom Finkbeiner Lab Galaxy tools and exposes them to Galaxy as an additional ToolShed repository. See Galaxy's guide to [adding tools](https://galaxyproject.org/admin/tools/add-tool-from-toolshed-tutorial/) for more info.
