# Galaxy Tool Shed
This project stores our custom Finkbeiner Lab Galaxy tools and exposes them to Galaxy as an additional Tool Shed repository. See Galaxy's guide to [adding tools](https://galaxyproject.org/admin/tools/add-tool-from-toolshed-tutorial/) for more info.


## Structure of this project
In Galaxy, each tool is in its own repository "shed". Each shed has its own tool or related tools, decoupled from the other sheds, and has its own versioning, dependencies,and metadata. This new structure, following Galaxy best practices, is different from the previous version of Galaxy used in the Finkbiener lab. The primary tradeoff between the two approaches is UI clarity verses dependency isolation. The advantage of the older approach is all of the finkbiener custom lab tools are grouped under one directory. This new approach gives up that UI clarity, as each tool will be in its own directory, but gets dependency isolation in exchange. So the libraries in a tool can only conflict within the tool itself, not across the libraries of all tools. This is tremendously useful for keeping these tools working. Their are additional minor benefits to this best practice, like being able to peel-off tools and publish them to the Galaxy community, or install just the ones you use.

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

# Shed Definition (shed.yml)
Each shed repository has a yaml defining the metadata about the tool.

```
name: tool1
owner: finkbeiner-lab
description: "Tool 1 developed by Finkbeiner Lab"
long_description: "This tool performs data processing and analysis tasks."
categories:
  - Data Analysis
  - Image Processing
homepage_url: "https://github.com/finkbeiner-lab/Galaxy_Tool_Shed/tool1"
remote_repository_url: "https://github.com/finkbeiner-lab/Galaxy_Tool_Shed"
```

# Tool Definition (tool_name.xml)
Each tool in a shed repository has an xml definition containing metadata about how to build, run, and test it. You'll notice that, by best practice, dependencies are usually pinned to specific versions. This has tradeoffs, but is appropriate in this case to keep things running smoothly for nontechnical users. Tool isolation will help mitigate technical debt pileup.

```
<tool id="tool1" name="Tool 1" version="1.0.0">
    <description>Tool 1 performs data processing and analysis tasks.</description>
    <requirements>
        <requirement type="package" version="1.19.2">numpy</requirement>
        <requirement type="package" version="1.1.3">pandas</requirement>
    </requirements>
    <command>python $tool1.py --input $input --output $output</command>
    <inputs>
        <param name="input" type="data" format="csv" label="Input File"/>
    </inputs>
    <outputs>
        <data name="output" format="txt" label="Output File"/>
    </outputs>
    <help>
        <![CDATA[
        Detailed help and usage instructions for Tool 1.
        ]]>
    </help>
    <tests>
        <test>
            <param name="input" value="test-data/test_input1.txt"/>
            <output name="output" file="expected_output1.txt"/>
        </test>
    </tests>
</tool>
```


## Tell Galaxy about our Tool Shed
This Tool Shed will be pulled into Galaxy by creating/modifying the Galaxy's `config/tool_sheds_conf.xml` with the following:
```
<?xml version="1.0"?>
<tool_sheds>
    <tool_shed name="FinkbeinerTool Shed" url="https://github.com/finkbeiner-lab/Galaxy_Tool_Shed" />
</tool_sheds>
```

Then Galaxy has to know to import this tool shed config file. We can create/modify the following to `config/galaxy.yml` to do so:
```
tool_sheds_config_file: config/tool_sheds_conf.xml
```

## Install the Tool
Tools are not usually installed by default just because they exist in a Tool Shed that Galaxy knows about. There are many Galaxy Tool Sheds, with thousands of available tools. So if your tool isn't showing up, it probably needs to be installed in Galaxy through the admin interface.
This project stores our custom Finkbeiner Lab Galaxy tools and exposes them to Galaxy as an additional Tool Shed repository. See Galaxy's guide to [adding tools](https://galaxyproject.org/admin/tools/add-tool-from-Tool Shed-tutorial/) for more info.
