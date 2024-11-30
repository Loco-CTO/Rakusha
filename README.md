<div align="center">
  <a href="https://raw.githubusercontent.com/Rystal-Team/Rystal-V6/main/assets/logo.png">
    <img src="https://raw.githubusercontent.com/Rystal-Team/Rystal-V6/main/assets/logo.png" alt="Logo" width="80" height="80">
  </a>
  <h3 align="center">Rakusha（楽シア）</h3>
  <p align="center">
    Rakusha is a simple ShareX server built with Flask. It allows users to upload, view, and manage files with ease.
    <br/>
    <br />
    <br />
    <a href="https://github.com/Rystal-Team/Rakusha/issues">Submit Issues</a> · <a href="https://github.com/Rystal-Team/Rakusha/releases">Releases</a>
  </p>
</div>

<div align="center">

[![GitHub Forks](https://img.shields.io/github/forks/Rystal-Team/Rakusha.svg?style=for-the-badge)](https://github.com/Rystal-Team/Rakusha)
[![GitHub Stars](https://img.shields.io/github/stars/Rystal-Team/Rakusha.svg?style=for-the-badge)](https://github.com/Rystal-Team/Rakusha)
[![License](https://img.shields.io/github/license/Rystal-Team/Rakusha.svg?style=for-the-badge)](https://github.com/Rystal-Team/Rakusha/blob/main/LICENSE)
[![Github Watchers](https://img.shields.io/github/watchers/Rystal-Team/Rakusha.svg?style=for-the-badge)](https://github.com/Rystal-Team/Rakusha)

</div>

## Key Features

- **File Upload**: Upload files directly to the server.
- **File Management**: View, delete, and manage uploaded files.
- **User Authentication**: Secure login and registration system.
- **Invite System**: Generate and manage invite codes for user registration.

**Note that this project is still in development and is not planned for production use.*

## Installation

### Prerequisites

- Python 3.8+
- Flask

### Setup

1. Clone the repository:

```bash
git clone https://github.com/Rystal-Team/Rakusha.git
cd Rakusha
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install the dependencies:

```bash
pip install -r 

requirements.txt
```

4. Set up the environment variables:

Create a `.env` file in the root directory and add the following:

```env
SECRET_KEY=your_secret_key
```

5. Initialize the database:

```bash
python -c 'from database import db_handler; db_handler.create_tables()'
```

6. Run the application:

```bash
python 

run.py
```

## Usage

### Uploading Files

You can upload files directly through the dashboard interface.

### Managing Files

View, delete, and manage your uploaded files through the dashboard.

### User Authentication

Secure login and registration system with invite code support.

## Contributing

We welcome contributions! Please fork the repository and submit pull requests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

<div align="center">
	<p><small>Copyright © 2024 <a href="https://rystal.net">Rystal</a>. All rights reserved.</small></p>
</div>
