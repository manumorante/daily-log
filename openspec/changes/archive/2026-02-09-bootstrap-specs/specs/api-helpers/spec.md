## ADDED Requirements

### Requirement: Generic fetch function
`fetch(url, headers, data=None)` SHALL make an HTTP request and return parsed JSON. When `data` is provided, it SHALL make a POST request; otherwise GET. It SHALL raise `urllib.error.URLError` or `urllib.error.HTTPError` on failure.

#### Scenario: Successful GET
- **WHEN** `fetch(url, headers)` is called with no data
- **THEN** it makes a GET request and returns the parsed JSON response

#### Scenario: Successful POST
- **WHEN** `fetch(url, headers, data=b'...')` is called with data
- **THEN** it makes a POST request with the data as body

#### Scenario: HTTP error
- **WHEN** the server returns a 4xx or 5xx status
- **THEN** `urllib.error.HTTPError` is raised

### Requirement: GitHub API helper
`github(path, token)` SHALL call `https://api.github.com/{path}` with Bearer token auth, GitHub v3 Accept header, and `User-Agent: daily-log`.

#### Scenario: Authenticated GitHub call
- **WHEN** `github("users/foo/events", token)` is called
- **THEN** it requests `https://api.github.com/users/foo/events` with `Authorization: Bearer {token}`

### Requirement: Shortcut API helper
`shortcut(path, token)` SHALL call `https://api.app.shortcut.com/api/v3/{path}` with `Shortcut-Token` header.

#### Scenario: Authenticated Shortcut call
- **WHEN** `shortcut("workflows", token)` is called
- **THEN** it requests `https://api.app.shortcut.com/api/v3/workflows` with `Shortcut-Token: {token}`

### Requirement: WakaTime API helper
`wakatime(path, api_key)` SHALL call `https://api.wakatime.com/api/v1/{path}` with HTTP Basic auth (api_key as username, empty password, base64 encoded).

#### Scenario: Authenticated WakaTime call
- **WHEN** `wakatime("users/current/summaries", key)` is called
- **THEN** it requests with `Authorization: Basic {base64(key:)}`
