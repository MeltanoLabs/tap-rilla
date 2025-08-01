# tap-rilla

`tap-rilla` is a Singer tap for the Rilla Voice API, built with the [Meltano SDK](https://sdk.meltano.com) for Singer Taps.

## Installation

Install from source:

```bash
pip install -e .
```

## Configuration

### Required Settings

- `api_key`: The API key to authenticate with the Rilla API

### Optional Settings

- `start_date`: The earliest date from which to pull data (YYYY-MM-DD format)
- `end_date`: The latest date from which to pull data (YYYY-MM-DD format). If not specified, defaults to today.
- `users`: An optional array of user email addresses to filter conversations. Only applies to the conversations stream. If provided and not empty, only conversation data for those users will be returned. If not provided or empty, all conversation data is returned.
- `date_type`: Date type to filter by. Options are `timeOfRecording` or `processedDate`. **Default: `timeOfRecording`**

### Configuration Examples

Basic configuration:
```yaml
api_key: your_api_key_here
start_date: '2024-01-01'
end_date: '2024-12-31'
```

Filter conversations for specific users:
```yaml
api_key: your_api_key_here
start_date: '2024-01-01'
users:
  - user1@company.com  
  - user2@company.com
```

Use processed date instead of recording date:
```yaml
api_key: your_api_key_here
start_date: '2024-01-01'
date_type: processedDate
```

A full list of supported settings and capabilities is available by running: `tap-rilla --about`

## Streams

The tap extracts data from the following Rilla API endpoints:

### conversations
- **Description**: Exports conversation data recorded during the specified time range
- **Endpoint**: `POST /export/conversations`
- **Supports user filtering**: Yes (via `users` config parameter)
- **Pagination**: Yes (25 records per page)
- **Primary Key**: `conversationId`

### teams  
- **Description**: Exports team data and usage during the specified time range
- **Endpoint**: `POST /export/teams`
- **Supports user filtering**: No
- **Pagination**: No
- **Primary Key**: `id`

### users
- **Description**: Exports user data and usage during the specified time range  
- **Endpoint**: `POST /export/users`
- **Supports user filtering**: No
- **Pagination**: No
- **Primary Key**: `id`

All streams support the `date_type` parameter with `timeOfRecording` as the default. You can optionally set `date_type: processedDate` to filter by processing date instead of recording date.

## Usage

You can easily run `tap-rilla` with the included `meltano.yml` project file.

1. Create a `.env` file with your API key:
```bash
TAP_RILLA_API_KEY=your_api_key_here
```

2. Install Meltano and the tap:
```bash
pip install meltano
meltano install
```

3. Test the tap:
```bash
meltano run tap-rilla target-jsonl
```

### Executing the Tap Directly

```bash
tap-rilla --version
tap-rilla --help
tap-rilla --config CONFIG --discover > ./catalog.json
```

## Developer Resources

### Initialize your Development Environment

```bash
pip install -e ".[dev]"
```

### Testing with Meltano

```bash
meltano run tap-rilla target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to develop and test this tap.