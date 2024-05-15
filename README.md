# Galaxy Tool Shed
This project stores our custom Finkbeiner Lab Galaxy tools and exposes them to Galaxy as an additional ToolShed repository. See Galaxy's guide to [adding tools](https://galaxyproject.org/admin/tools/add-tool-from-toolshed-tutorial/) for more info.

# Structure
There is an outer ToolShed repository that contains references to each tool's individual repository. This repository composition structure is driven by the recommended approach from the Galaxy developers.
<em>With regard to Galaxy tools, a repository should only contain one. The reasons for this are related to tool versioning and reproducibility. Repository owners can define relationships between repositories, with a single repository requiring any number of additional repositories. This feature allows for multiple related tools and utilities to be installed with a single repository selected from the ToolShed.</em> [Repository Best Practices](https://galaxyproject.org/toolshed/repository-population-best-practices1/)

