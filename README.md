# Wishlists Service

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
[![Build Status](https://github.com/CSCI-GA-2820-SP24-003/wishlists/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-SP24-003/wishlists/actions)

## Overview

This service includes models, routes, and tests for managing wishlists and wishlist items. It allows users to create, update, delete, and view wishlists and wishlist items through a RESTful API coded in Flask. This project is designed with DevOps practices in mind, emphasizing automation, continuous integration, and providing a clear, comprehensive test suite to ensure code quality and reliability.

**Tip: For a streamlined development experience, open the project in DevContainers with VSCode.** 

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
pyproject.toml      - Poetry list of Python libraries required by your code

service/                   - service python package
├── __init__.py            - package initializer
├── config.py              - configuration parameters
├── models
    ├── __init__.py        - model initializer
    ├── persistent_base.py - Base class
    ├── wishlist.py        - Wishlist model
    ├── wishlist_item.py   - Wishlist Item model
├── routes.py              - module with service routes
└── common                 - common code package
    ├── cli_commands.py    - Flask command to recreate all tables
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/                     - test cases package
├── __init__.py            - package initializer
├── factories.py           - test factories
├── test_cli_commands.py   - test suite for the CLI
├── test_routes.py         - test suite for service routes
├── test_wishlist_item.py  - test suite for wishlist item model
└── test_wishlist.py       - test suite for wishlist model
```

## API Endpoints

```text
Endpoint              Methods  Rule                              
--------------------  -------  ----------------------------------
index                 GET      / 

create_wishlist       POST     /wishlists                        
create_wishlist_item  POST     /wishlists/<int:wishlist_id>/items

read_wishlist         GET      /wishlists/<int:id>
read_wishlist_item    GET      /wishlists/<int:wishlist_id>/items/<int:item_id>

update_wishlist       PUT      /wishlists/<int:wishlist_id>
update_wishlist_item  PUT      /wishlists/<int:wishlist_id>/items/<int:item_id>

delete_wishlist       DELETE   /wishlists/<int:id>
delete_wishlist_item  DELETE   /wishlists/<int:wishlist_id>/items/<int:item_id>

list_wishlists        GET      /wishlists
list_wishlist_items   GET      /wishlists/<int:wishlist_id>/items

static                GET      /static/<path:filename>
```

## Testing

```bash
make test
```

## Running the server

```bash
make run
```

## License

Copyright (c) 2016, 2024 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
