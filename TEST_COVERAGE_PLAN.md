# Test Coverage Plan for Icosa Gallery

## Overview

This document outlines the comprehensive test coverage plan for the Icosa Gallery Django application, moving from 0% coverage to extensive test coverage across all major components.

## Testing Infrastructure

### Framework & Tools
- **pytest** 8.3.4 - Main testing framework
- **pytest-django** 4.9.0 - Django integration for pytest
- **pytest-cov** 6.0.0 - Coverage reporting
- **factory-boy** 3.3.1 - Test fixture factories
- **faker** 33.1.0 - Fake data generation
- **pytest-mock** 3.14.0 - Mocking utilities

### Configuration Files
- `pytest.ini` - Pytest configuration with Django settings, markers, and coverage options
- `.coveragerc` - Coverage exclusions and reporting configuration
- `conftest.py` - Shared fixtures and test setup

## Test Structure

```
django/icosa/tests/
├── __init__.py
├── conftest.py                    # Global fixtures
├── fixtures/
│   ├── __init__.py
│   └── factories.py               # Factory-boy model factories
├── test_models/                   # Model unit tests
│   ├── __init__.py
│   ├── test_user.py              # 25+ tests
│   ├── test_asset.py             # 60+ tests
│   ├── test_format.py            # 45+ tests
│   ├── test_collection.py        # 45+ tests
│   ├── test_oauth.py             # 45+ tests
│   ├── test_asset_owner.py       # 35+ tests
│   ├── test_tag_and_like.py      # 30+ tests
│   └── test_device_code.py       # 30+ tests
├── test_api/                      # API endpoint tests
│   ├── __init__.py
│   ├── test_assets_api.py        # 50+ tests
│   ├── test_users_api.py         # 70+ tests
│   └── test_login_api.py         # 50+ tests
├── test_forms/                    # Form validation tests
│   ├── __init__.py
│   └── test_asset_forms.py       # 45+ tests
├── test_helpers/                  # Helper function tests
│   ├── __init__.py
│   ├── test_file_helpers.py      # 80+ tests
│   └── test_snowflake.py         # 60+ tests
├── test_views/                    # View tests (pending)
│   └── __init__.py
└── test_commands/                 # Management command tests (pending)
    └── __init__.py
```

## Test Coverage by Component

### 1. Models (315+ tests)

#### User Model (25 tests)
- User creation and authentication
- Device code generation with exclusion rules
- JWT access token generation and expiration
- URL generation with ownership handling
- Email uniqueness constraints
- SuperUser creation

#### Asset Model (60 tests)
- Asset creation with various visibility states
- `is_published` and `model_is_editable` properties
- Slug generation from names
- License handling (all variants: CC-BY, CC0, All Rights Reserved, v3/v4)
- URL generation (view, edit, delete)
- Ownership validation
- Search text denormalization
- Format type denormalization
- Rank calculation and view tracking
- Like time denormalization
- Preferred viewer format selection
- Tag relationships
- Thumbnail handling
- License icon generation

#### Format & Resource Models (45 tests)
- Format creation with different types (GLB, OBJ, FBX, GLTF2)
- Root resource management
- Resource data aggregation for downloads
- CORS-allowed resource handling
- Format role labels
- Resource URL handling (local vs external)
- Archive.org URL transformation
- Remote host detection and CORS validation

#### Collection Models (45 tests)
- AssetCollection creation with auto-generated URLs
- Visibility management
- Many-to-many asset relationships
- Thumbnail URL generation
- AssetCollectionAsset ordering
- Cascade deletion behavior

#### OAuth2 Models (45 tests)
- Oauth2Client creation and validation
- Oauth2Code authorization flow with PKCE
- Oauth2Token lifecycle, expiration, and revocation
- Unique constraints
- Token type and scope handling

#### AssetOwner Model (35 tests)
- Owner creation and URL uniqueness
- Django user relationship
- Claimed vs unclaimed owner handling
- Owner merging functionality
- Display name resolution
- get_unclaimed_for_user manager method
- Cascade deletion behavior

#### Tag & UserLike Models (30 tests)
- Tag creation, uniqueness, and ordering
- Tag-to-asset many-to-many relationships
- UserLike creation and timestamps
- Cascade deletion for likes
- Chronological ordering
- Like count aggregation

#### DeviceCode Model (30 tests)
- Device code creation and validation
- String representation
- Max length enforcement (6 characters)
- User relationship
- Expiry functionality (valid/expired detection)
- Querying by validity and device code
- Case-insensitive search
- User cascade deletion
- Multiple codes per user
- Alphanumeric validation
- get_or_create pattern
- Short and long expiry handling

### 2. API Endpoints (170+ tests)

#### Asset Retrieval
- GET /api/assets/{asset} for public/unlisted/private assets
- 404 handling for non-existent and unauthorized assets
- Response schema validation

#### Asset Listing
- GET /api/assets/ with pagination
- Filtering by category, format, curated status
- Excluding private and all-rights-reserved assets
- Ordering by likes, views, date
- Keyword search

#### Upload State
- GET /api/assets/{asset}/upload_state
- Authentication and authorization checks

#### Helper Functions
- user_owns_asset validation
- user_can_view_asset permission checks
- Public vs private access control

#### Users API (70 tests)
- GET /api/users/me endpoint (authenticated and unauthenticated)
- PATCH /api/users/me endpoint (update display name, URL, description)
- URL uniqueness validation
- Multiple owners error handling
- GET /api/users/me/assets endpoint (pagination, filtering)
- POST /api/users/me/assets endpoint (asset creation, owner auto-creation)
- GET /api/users/me/assets/{asset} endpoint (specific asset retrieval)
- DELETE /api/users/me/assets/{asset} endpoint (asset deletion, media hiding)
- GET /api/users/me/likedassets endpoint (liked assets, visibility filtering)

#### Login API (50 tests)
- POST /api/login/device_login endpoint
- Valid device code authentication
- Expired and invalid code handling
- Code deletion after use
- Case-insensitive matching
- JWT token generation and validation
- Multiple codes error handling
- Empty code and missing parameter validation
- Token expiry verification
- User association in token
- Whitespace and special character handling

### 3. Forms (45+ tests)

#### AssetUploadForm
- Valid file extensions (glb, zip, ksplat, ply, stl, usdz, vox)
- File extension validation
- MIME type validation
- Required field validation

#### AssetReportForm
- Reason for reporting (required, max 1000 chars)
- Asset URL (required)
- Contact email (optional)
- Field validation and error handling

#### AssetPublishForm
- Name and license requirements
- Creative Commons license choices
- License field disabled for published CC assets
- License field enabled for private assets

#### AssetEditForm
- Required name field
- Editable vs non-editable asset handling
- Conditional field inclusion
- License upgrade from v3 to v4
- Thumbnail override field

### 4. Helpers (140+ tests)

#### get_content_type Function
- Content type detection for all supported formats
- GLB, GLTF, OBJ, FBX, images
- New formats (KSPLAT, PLY, STL, USDZ, VOX)
- Unknown extension handling

#### validate_file Function
- Validation for all main file types
- Detection of main vs helper files
- Image file validation
- Invalid extension rejection
- GLTF version detection (1.0 vs 2.0)

#### is_gltf2 Function
- glTF 2.0 detection
- glTF 1.0 detection
- JSON structure parsing

#### Constants Testing
- VALID_FORMAT_TYPES completeness
- CONTENT_TYPE_MAP accuracy
- IMAGE_REGEX pattern matching

#### Snowflake ID Generation (60 tests)
- generate_snowflake function:
  * Integer return, positive IDs, uniqueness
  * Incremental ordering
  * Timestamp component extraction
  * Process ID component (bits 4-21, capped at 0x3FFFF)
  * Counter component (bits 0-3, wraps at 15)
  * 64-bit layout validation

- get_timestamp function:
  * ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)
  * Parseability to datetime
  * Recent timestamp validation

- get_timestamp_raw function:
  * Integer millisecond timestamp
  * After ICOSA_EPOCH validation
  * Correct bit extraction

- get_snowflake_timestamp function:
  * Datetime object return
  * Year range validation (2020-2100)

- get_snowflake_timestamp_raw function:
  * Consistency with get_timestamp_raw

- ICOSA_EPOCH constant:
  * Value validation (1609459200000 = 2020-01-01)

- Round-trip tests:
  * Generation and extraction consistency
  * Temporal ordering
  * Method consistency

- Edge cases:
  * Max process ID capping
  * Zero process ID
  * Rapid generation (100 IDs)

## Test Factories

Comprehensive factory-boy factories for all models:

- **UserFactory** / SuperUserFactory
- **AssetFactory** (with Private/Unlisted variants)
- **AssetOwnerFactory**
- **FormatFactory** (with GLB/OBJ/FBX variants)
- **ResourceFactory**
- **TagFactory**
- **UserLikeFactory**
- **AssetCollectionFactory** / AssetCollectionAssetFactory
- **Oauth2ClientFactory** / Oauth2CodeFactory / Oauth2TokenFactory
- **DeviceCodeFactory**
- **FormatRoleLabelFactory**

Helper functions for complex scenarios:
- `create_asset_with_formats()`
- `create_asset_with_likes()`
- `create_collection_with_assets()`

## Fixtures (conftest.py)

Global fixtures available to all tests:
- `client` - Django test client
- `authenticated_client` - Authenticated test client
- `user` - Regular user
- `superuser` - Admin user
- `users` - Multiple users
- `sample_image` - Test image file
- `sample_glb_file` - Test GLB file
- `api_client` - API client
- `authenticated_api_client` - Authenticated API client
- `mock_storage` - Mock storage backend

## Test Markers

Tests are organized with pytest markers:
- `@pytest.mark.django_db` - Database access
- `@pytest.mark.models` - Model tests
- `@pytest.mark.api` - API tests
- `@pytest.mark.forms` - Form tests
- `@pytest.mark.helpers` - Helper function tests
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow-running tests

## Running Tests

### Run All Tests
```bash
cd django
pytest
```

### Run Specific Test Module
```bash
pytest icosa/tests/test_models/test_asset.py
```

### Run Tests by Marker
```bash
pytest -m models
pytest -m api
pytest -m forms
```

### Generate Coverage Report
```bash
pytest --cov=icosa --cov-report=html --cov-report=term-missing
```

### Run Fast Tests Only
```bash
pytest -m "not slow"
```

## Coverage Goals

### Current Status: ~670+ tests
- ✅ Models: Comprehensive coverage (315+ tests)
  * User, Asset, Format, Resource, Collection
  * OAuth2, AssetOwner, Tag, UserLike, DeviceCode
- ✅ API Endpoints: Extensive coverage (170+ tests)
  * Assets API, Users API, Login API
  * Authentication, authorization, pagination
- ✅ Forms: All main forms tested (45+ tests)
  * Upload, Edit, Publish, Report forms
- ✅ Helpers: Complete coverage (140+ tests)
  * File validation and format detection
  * Snowflake ID generation and extraction
- ⏳ Views: Pending
- ⏳ Management Commands: Pending (17 commands)
- ⏳ Middleware: Pending
- ⏳ Template Tags: Pending

### Future Additions
1. **View Tests** - Test all main views, auth views, collection views
2. **Management Command Tests** - Test 17 management commands
3. **Middleware Tests** - Test custom middleware
4. **Template Tag Tests** - Test custom template tags
5. **Integration Tests** - End-to-end workflow tests
6. **Performance Tests** - Load and stress testing

## Best Practices

1. **Use factories** instead of creating models directly
2. **Use fixtures** for common test data
3. **Mark tests appropriately** for organization and selective running
4. **Test edge cases** and error conditions
5. **Mock external dependencies** (storage, APIs)
6. **Keep tests isolated** - each test should be independent
7. **Use descriptive test names** - clearly state what is being tested
8. **Test both success and failure cases**

## Continuous Integration

Tests should be run:
- Before every commit
- On every pull request
- On every push to main branch
- Nightly for full test suite with slow tests

## Maintenance

- Update tests when models change
- Add tests for new features
- Maintain factory definitions
- Keep fixture data realistic
- Review and update this plan quarterly
